"""
推荐系统离线计算脚本
定时运行（如每天凌晨），预计算：
1. TF-IDF 矩阵
2. 商品聚类（K-Means）
3. 合理价格区间
4. 用户兴趣标签
"""
import os
import sys
import pickle
from collections import defaultdict, Counter

import numpy as np
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# 添加项目根目录到 path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app, db
from app.models.models import (
    Item, UserAction, User, Order, Category,
    ItemEmbedding, UserInterest
)
from app.services.text_processor import ItemTextProcessor, TextCleaner

MODEL_DIR = os.path.join(os.path.dirname(__file__), '../data/models')
CLUSTER_K = 8


def ensure_dir():
    os.makedirs(MODEL_DIR, exist_ok=True)


def save_model(name, data):
    path = os.path.join(MODEL_DIR, f'{name}.pkl')
    with open(path, 'wb') as f:
        pickle.dump(data, f)
    print(f'  -> 已保存: {path}')


def tokenize_zh(text):
    """中文分词（使用文本处理服务）"""
    if not text:
        return ''
    cleaned = TextCleaner.clean_for_vectorization(text)
    return ' '.join(jieba.cut(cleaned))

def build_tfidf_matrix():
    """步骤1: 构建 TF-IDF 矩阵并持久化（使用文本处理服务）"""
    print('\n[1/4] 构建 TF-IDF 矩阵...')
    items = Item.query.filter(Item.status == 'on_sale').all()
    if not items:
        print('  无在售商品，跳过')
        return

    item_ids = [i.id for i in items]
    corpus = []
    for item in items:
        # 使用文本处理服务进行清洗和分词
        processed_text = ItemTextProcessor.get_item_text_for_vectorization(
            item.name,
            item.description,
            item.condition
        )
        corpus.append(processed_text)

    vectorizer = TfidfVectorizer(max_features=5000)
    tfidf_matrix = vectorizer.fit_transform(corpus)

    save_model('tfidf_matrix', {
        'vectorizer': vectorizer,
        'matrix': tfidf_matrix,
        'item_ids': item_ids
    })

    # 同时将向量写入数据库 item_embeddings 表
    for idx, item_id in enumerate(item_ids):
        vec = tfidf_matrix[idx].toarray().flatten().tolist()
        # 截断到前50维降低存储
        vec_short = vec[:50]
        existing = ItemEmbedding.query.filter_by(item_id=item_id).first()
        if existing:
            existing.embedding = vec_short
        else:
            db.session.add(ItemEmbedding(item_id=item_id, embedding=vec_short))
    db.session.commit()
    print(f'  已处理 {len(items)} 个商品的 TF-IDF 向量')


def build_item_clusters():
    """步骤2: K-Means 商品聚类"""
    print('\n[2/4] 构建商品聚类...')
    tfidf_data = None
    tfidf_path = os.path.join(MODEL_DIR, 'tfidf_matrix.pkl')
    if os.path.exists(tfidf_path):
        with open(tfidf_path, 'rb') as f:
            tfidf_data = pickle.load(f)

    if tfidf_data is None:
        print('  TF-IDF 矩阵不存在，跳过聚类')
        return

    matrix = tfidf_data['matrix']
    item_ids = tfidf_data['item_ids']

    if len(item_ids) < CLUSTER_K:
        k = max(2, len(item_ids))
    else:
        k = CLUSTER_K

    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(matrix.toarray())

    item_clusters = {}  # item_id -> cluster_id
    cluster_items = defaultdict(list)  # cluster_id -> [item_ids]
    for idx, item_id in enumerate(item_ids):
        cluster_id = int(labels[idx])
        item_clusters[item_id] = cluster_id
        cluster_items[cluster_id].append(item_id)

    save_model('item_clusters', {
        'kmeans': kmeans,
        'item_clusters': item_clusters,
        'cluster_items': dict(cluster_items)
    })
    print(f'  已将 {len(item_ids)} 个商品聚为 {k} 个簇')

def build_price_reference():
    """步骤3: 计算各类别合理价格区间"""
    print('\n[3/4] 计算合理价格区间...')
    categories = Category.query.all()
    price_ref = {}

    for cat in categories:
        # 优先用已成交订单价格
        completed = db.session.query(Order.amount).join(
            Item, Order.item_id == Item.id
        ).filter(
            Item.category_id == cat.id,
            Order.status == 'completed'
        ).all()

        if completed:
            prices = [float(o.amount) for o in completed]
        else:
            # 降级用在售商品价格
            items = Item.query.filter_by(
                category_id=cat.id, status='on_sale'
            ).all()
            prices = [float(i.price) for i in items]

        if not prices:
            continue

        prices_arr = np.array(prices)
        price_ref[str(cat.id)] = {
            'low': round(float(np.percentile(prices_arr, 25)), 2),
            'high': round(float(np.percentile(prices_arr, 75)), 2),
            'avg': round(float(np.mean(prices_arr)), 2),
            'count': len(prices)
        }

    save_model('price_reference', price_ref)
    print(f'  已计算 {len(price_ref)} 个类别的价格区间')


def build_user_interests():
    """步骤4: 更新用户兴趣标签"""
    print('\n[4/4] 更新用户兴趣标签...')

    # 批量预加载所有 item_id -> category_id 映射，避免 N+1
    item_cat_map = dict(
        db.session.query(Item.id, Item.category_id)
        .filter(Item.category_id.isnot(None)).all()
    )

    users = User.query.all()
    count = 0

    for user in users:
        actions = UserAction.query.filter_by(user_id=user.id).all()
        if not actions:
            continue

        # 统计用户交互的类别频次
        cat_counter = Counter()
        for a in actions:
            cat_id = item_cat_map.get(a.item_id)
            if cat_id:
                w = 3 if a.action_type == 'fav' else 1
                cat_counter[cat_id] += w

        # 取 top3 类别写入 user_interests
        top_cats = [cat_id for cat_id, _ in cat_counter.most_common(3)]

        # 清除旧兴趣
        UserInterest.query.filter_by(user_id=user.id).delete()
        for cat_id in top_cats:
            db.session.add(UserInterest(user_id=user.id, category_id=cat_id))
        count += 1

    db.session.commit()
    print(f'  已更新 {count} 个用户的兴趣标签')


def main():
    print('=' * 50)
    print('推荐系统离线计算开始')
    print('=' * 50)

    ensure_dir()
    app = create_app()

    with app.app_context():
        build_tfidf_matrix()
        build_item_clusters()
        build_price_reference()
        build_user_interests()

    print('\n' + '=' * 50)
    print('离线计算完成!')
    print('=' * 50)


if __name__ == '__main__':
    main()

