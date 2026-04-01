"""
推荐系统离线计算脚本
定时运行（如每天凌晨），预计算：
1. TF-IDF 矩阵
2. 潜在语义向量和近邻索引
3. 商品聚类（K-Means）
4. 合理价格区间
5. 用户兴趣标签
"""
import os
import sys
import pickle
from collections import defaultdict, Counter

import numpy as np
import jieba
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors

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
EMBEDDING_DIM = 64
SEMANTIC_NEIGHBORS = 80


def ensure_dir():
    os.makedirs(MODEL_DIR, exist_ok=True)


def save_model(name, data):
    path = os.path.join(MODEL_DIR, f'{name}.pkl')
    with open(path, 'wb') as f:
        pickle.dump(data, f)
    print(f'  -> 已保存: {path}')


def load_model(name):
    path = os.path.join(MODEL_DIR, f'{name}.pkl')
    if not os.path.exists(path):
        return None
    with open(path, 'rb') as f:
        return pickle.load(f)


def normalize_vectors(vectors):
    """L2 归一化，便于余弦近邻检索"""
    vectors = np.asarray(vectors, dtype=float)
    if vectors.size == 0:
        return vectors
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vectors / norms


def tokenize_zh(text):
    """中文分词（使用文本处理服务）"""
    if not text:
        return ''
    cleaned = TextCleaner.clean_for_vectorization(text)
    return ' '.join(jieba.cut(cleaned))

def build_tfidf_matrix():
    """步骤1: 构建 TF-IDF 矩阵并持久化（使用文本处理服务）"""
    print('\n[1/5] 构建 TF-IDF 矩阵...')
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
    print(f'  已处理 {len(items)} 个商品的 TF-IDF 向量')


def build_semantic_index():
    """步骤2: 构建潜在语义向量和近邻索引"""
    print('\n[2/5] 构建潜在语义索引...')

    tfidf_data = load_model('tfidf_matrix')
    if tfidf_data is None:
        print('  TF-IDF 矩阵不存在，跳过')
        return

    tfidf_matrix = tfidf_data.get('matrix')
    item_ids = tfidf_data.get('item_ids', [])
    if tfidf_matrix is None or not item_ids:
        print('  TF-IDF 数据不完整，跳过')
        return

    n_items, n_features = tfidf_matrix.shape
    dense_vectors = tfidf_matrix.toarray()
    svd = None
    explained = 0.0

    max_components = min(n_items - 1, n_features - 1, EMBEDDING_DIM)
    if max_components >= 2:
        svd = TruncatedSVD(n_components=max_components, random_state=42)
        dense_vectors = svd.fit_transform(tfidf_matrix)
        explained = float(svd.explained_variance_ratio_.sum())

    dense_vectors = normalize_vectors(dense_vectors)

    nn_model = None
    neighbors = {}
    if len(item_ids) >= 2:
        neighbor_count = min(SEMANTIC_NEIGHBORS + 1, len(item_ids))
        nn_model = NearestNeighbors(
            n_neighbors=neighbor_count,
            metric='cosine',
            algorithm='brute'
        )
        nn_model.fit(dense_vectors)
        distances, indices = nn_model.kneighbors(dense_vectors, n_neighbors=neighbor_count)

        for row_idx, item_id in enumerate(item_ids):
            scored_neighbors = []
            for dist, neighbor_idx in zip(distances[row_idx], indices[row_idx]):
                neighbor_id = item_ids[neighbor_idx]
                if neighbor_id == item_id:
                    continue
                scored_neighbors.append((neighbor_id, round(1 - float(dist), 6)))
                if len(scored_neighbors) >= SEMANTIC_NEIGHBORS:
                    break
            neighbors[item_id] = scored_neighbors

    save_model('semantic_index', {
        'item_ids': item_ids,
        'vectors': dense_vectors.tolist(),
        'svd': svd,
        'nn_model': nn_model,
        'neighbors': neighbors,
        'explained_variance': explained,
        'embedding_dim': int(dense_vectors.shape[1]) if dense_vectors.ndim == 2 else 0
    })

    ItemEmbedding.query.delete()
    for idx, item_id in enumerate(item_ids):
        db.session.add(ItemEmbedding(
            item_id=item_id,
            embedding=dense_vectors[idx].astype(float).tolist()
        ))
    db.session.commit()

    print(
        f'  已写入 {len(item_ids)} 个商品向量，维度 {dense_vectors.shape[1]}，'
        f'解释方差 {explained:.2%}'
    )


def build_item_clusters():
    """步骤2: K-Means 商品聚类"""
    print('\n[3/5] 构建商品聚类...')
    semantic_data = load_model('semantic_index')
    tfidf_data = load_model('tfidf_matrix')

    if semantic_data is not None and semantic_data.get('vectors') and semantic_data.get('item_ids'):
        matrix = np.array(semantic_data['vectors'], dtype=float)
        item_ids = semantic_data['item_ids']
    elif tfidf_data is not None and tfidf_data.get('matrix') is not None and tfidf_data.get('item_ids'):
        matrix = tfidf_data['matrix'].toarray()
        item_ids = tfidf_data['item_ids']
    else:
        print('  向量矩阵不存在，跳过聚类')
        return

    if len(item_ids) == 1:
        save_model('item_clusters', {
            'kmeans': None,
            'item_clusters': {item_ids[0]: 0},
            'cluster_items': {0: [item_ids[0]]}
        })
        print('  仅有 1 个商品，跳过 K-Means，使用单簇兜底')
        return

    k = min(CLUSTER_K, len(item_ids))
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(matrix)

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
    print('\n[4/5] 计算合理价格区间...')
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
    print('\n[5/5] 更新用户兴趣标签...')

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
        build_semantic_index()
        build_item_clusters()
        build_price_reference()
        build_user_interests()

    print('\n' + '=' * 50)
    print('离线计算完成!')
    print('=' * 50)


if __name__ == '__main__':
    main()
