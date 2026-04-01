"""
校园二手交易推荐系统核心引擎
架构：多路召回 -> 精排打分 -> 业务重排
"""
import json
import math
import pickle
import os
from collections import defaultdict, Counter
from datetime import datetime, timedelta

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

import jieba

from app import db, redis_client
from app.services.text_processor import ItemTextProcessor, TextCleaner
from app.models.models import Item, UserAction, User, Order

# ==================== 常量 ====================
RECALL_LIMIT = 200          # 召回候选集上限
FINAL_LIMIT = 60            # 最终推荐数
CF_TOPK = 50                # 协同过滤召回数
CONTENT_TOPK = 50           # 内容召回数
SEMANTIC_TOPK = 60          # 潜在语义召回数
HOT_TOPK = 30               # 热度召回数
CLUSTER_K = 8               # 聚类簇数
PRICE_BOOST = 1.2           # 合理定价提权系数
PRICE_PENALTY = 0.8         # 定价偏离降权系数
DIVERSITY_PENALTY = 0.6     # 同类打散降权系数
MAX_SAME_CATEGORY = 3       # 同类最大连续数
CACHE_TTL = int(os.getenv('RECOMMEND_CACHE_TTL', '600'))  # Redis 缓存默认 10 分钟
MODEL_DIR = os.path.join(os.path.dirname(__file__), '../../data/models')


def _get_user_school(user_id):
    """获取用户的学校名称，用于校园隔离过滤"""
    if not user_id:
        return None
    user = User.query.get(user_id)
    return user.school_name if user else None


def _school_item_ids_filter(school_name):
    """返回属于指定学校卖家的在售商品 ID 集合"""
    if not school_name:
        return None
    rows = db.session.query(Item.id).join(User, Item.seller_id == User.id).filter(
        User.school_name == school_name,
        Item.status == 'on_sale'
    ).all()
    return set(r[0] for r in rows)


def _effective_school_item_ids(user_id, school_name):
    """
    返回有效的校园隔离集合。
    如果同校只有用户自己的商品，则自动放宽为全站推荐，避免推荐结果为空。
    """
    school_ids = _school_item_ids_filter(school_name)
    if school_ids is None:
        return None
    other_item = db.session.query(Item.id).join(User, Item.seller_id == User.id).filter(
        User.school_name == school_name,
        Item.status == 'on_sale',
        Item.seller_id != int(user_id)
    ).first()
    if other_item is None:
        return None
    return school_ids


# ==================== 工具函数 ====================
def tokenize_zh(text):
    """中文分词（使用文本处理服务）"""
    if not text:
        return ''
    cleaned = TextCleaner.clean_for_vectorization(text)
    return ' '.join(jieba.cut(cleaned))


def get_item_text(item):
    """拼接商品文本特征（使用文本处理服务）"""
    return ItemTextProcessor.get_item_text_for_vectorization(
        item.name,
        item.description,
        item.condition
    )


def safe_load_model(name):
    """安全加载 pickle 模型"""
    path = os.path.join(MODEL_DIR, f'{name}.pkl')
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return pickle.load(f)
    return None


def _normalize_vector(vector):
    """将单个向量归一化，便于余弦相似度/近邻检索"""
    vector = np.asarray(vector, dtype=float).reshape(-1)
    if vector.size == 0:
        return None
    norm = np.linalg.norm(vector)
    if norm == 0:
        return None
    return vector / norm


def _ranked_source_scores(item_ids, weight):
    """按名次衰减生成召回分，便于多路融合"""
    if weight <= 0:
        return {}
    scores = {}
    for rank, item_id in enumerate(item_ids):
        scores[item_id] = scores.get(item_id, 0.0) + weight / math.log2(rank + 2)
    return scores


def _resolve_recall_weights(action_count, sources):
    """
    根据用户活跃度动态调整多路召回权重。
    零/低行为用户提高热度和聚类权重，活跃用户提高 CF/语义权重。
    """
    if action_count <= 0:
        base_weights = {
            'hot': 0.60,
            'semantic': 0.15,
            'content': 0.10,
            'cluster': 0.15,
            'cf': 0.0,
        }
    elif action_count < 5:
        base_weights = {
            'hot': 0.22,
            'semantic': 0.28,
            'content': 0.18,
            'cluster': 0.17,
            'cf': 0.15,
        }
    elif action_count < 15:
        base_weights = {
            'hot': 0.14,
            'semantic': 0.32,
            'content': 0.18,
            'cluster': 0.10,
            'cf': 0.26,
        }
    else:
        base_weights = {
            'hot': 0.10,
            'semantic': 0.35,
            'content': 0.15,
            'cluster': 0.08,
            'cf': 0.32,
        }

    active_weights = {
        name: weight
        for name, weight in base_weights.items()
        if sources.get(name)
    }
    total = sum(active_weights.values())
    if total <= 0:
        return {}
    return {name: weight / total for name, weight in active_weights.items()}

# ==================== 1. 召回层 ====================

class RecallEngine:
    """多路召回引擎"""

    @staticmethod
    def collaborative_filtering_recall(user_id, limit=CF_TOPK):
        """
        Item-CF 协同过滤召回
        逻辑：找到用户交互过的商品 -> 找到也交互过这些商品的其他用户 -> 按相似度加权取他们交互的其他商品
        """
        # 当前用户交互过的商品
        user_actions = UserAction.query.filter_by(user_id=user_id).all()
        if not user_actions:
            return []
        user_item_ids = set(a.item_id for a in user_actions)

        # 找到也交互过这些商品的相似用户
        similar_user_actions = UserAction.query.filter(
            UserAction.item_id.in_(user_item_ids),
            UserAction.user_id != user_id
        ).all()

        if not similar_user_actions:
            return []

        # 计算每个相似用户与当前用户的重叠度（共同交互商品数）
        user_overlap = Counter()
        for a in similar_user_actions:
            user_overlap[a.user_id] += 1

        # 找相似用户交互的其他商品（排除当前用户已交互的）
        similar_user_ids = set(a.user_id for a in similar_user_actions)
        other_actions = UserAction.query.filter(
            UserAction.user_id.in_(similar_user_ids),
            ~UserAction.item_id.in_(user_item_ids)
        ).all()

        weight_map = {'fav': 3, 'view': 1, 'search': 1}
        candidate_scores = defaultdict(float)
        for action in other_actions:
            action_weight = weight_map.get(action.action_type, 1)
            similarity = user_overlap.get(action.user_id, 1)
            candidate_scores[action.item_id] += action_weight * similarity

        sorted_items = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)
        return [item_id for item_id, _ in sorted_items[:limit]]

    @staticmethod
    def content_based_recall(user_id, limit=CONTENT_TOPK):
        """
        TF-IDF 内容召回
        逻辑：用户历史交互商品的文本 -> TF-IDF向量 -> 与全部在售商品计算余弦相似度
        """
        # 加载预计算的 TF-IDF 模型
        tfidf_data = safe_load_model('tfidf_matrix')
        if tfidf_data is None:
            return RecallEngine._fallback_content_recall(user_id, limit)

        vectorizer = tfidf_data.get('vectorizer')
        tfidf_matrix = tfidf_data.get('matrix')
        item_ids = tfidf_data.get('item_ids')
        if vectorizer is None or tfidf_matrix is None:
            return RecallEngine._fallback_content_recall(user_id, limit)

        # 用户交互过的商品
        user_actions = UserAction.query.filter_by(user_id=user_id).all()
        if not user_actions:
            return []
        user_item_ids = set(a.item_id for a in user_actions)
        item_id_to_idx = {iid: idx for idx, iid in enumerate(item_ids)}

        # 构建用户兴趣向量（交互商品向量的加权平均）
        weight_map = {'fav': 3, 'view': 1}
        vectors = []
        weights = []
        for a in user_actions:
            if a.item_id in item_id_to_idx:
                idx = item_id_to_idx[a.item_id]
                vectors.append(tfidf_matrix[idx].toarray().flatten())
                weights.append(weight_map.get(a.action_type, 1))

        if not vectors:
            return []

        weights = np.array(weights, dtype=float)
        weights /= weights.sum()
        user_vector = np.average(vectors, axis=0, weights=weights).reshape(1, -1)

        # 计算与所有商品的相似度
        similarities = cosine_similarity(user_vector, tfidf_matrix).flatten()
        scored = []
        for idx, score in enumerate(similarities):
            iid = item_ids[idx]
            if iid not in user_item_ids:
                scored.append((iid, float(score)))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [iid for iid, _ in scored[:limit]]

    @staticmethod
    def semantic_recall(user_id, limit=SEMANTIC_TOPK):
        """
        潜在语义召回
        逻辑：离线构建稠密向量 -> 在线聚合用户兴趣向量 -> 近邻检索
        """
        semantic_data = safe_load_model('semantic_index')
        if semantic_data is None:
            return []

        item_ids = semantic_data.get('item_ids', [])
        vectors = semantic_data.get('vectors')
        nn_model = semantic_data.get('nn_model')
        if not item_ids or vectors is None:
            return []

        user_actions = UserAction.query.filter_by(user_id=user_id).order_by(
            UserAction.created_at.desc()
        ).all()
        if not user_actions:
            return []

        item_id_to_idx = {iid: idx for idx, iid in enumerate(item_ids)}
        user_item_ids = set(a.item_id for a in user_actions)
        weight_map = {'fav': 3.0, 'view': 1.2, 'search': 0.8}

        user_vectors = []
        weights = []
        for action_rank, action in enumerate(user_actions[:50]):
            idx = item_id_to_idx.get(action.item_id)
            if idx is None:
                continue
            vector = np.asarray(vectors[idx], dtype=float)
            if vector.size == 0:
                continue
            recency_decay = max(0.35, 1 - action_rank * 0.04)
            user_vectors.append(vector)
            weights.append(weight_map.get(action.action_type, 1.0) * recency_decay)

        if not user_vectors:
            return []

        user_vector = _normalize_vector(np.average(
            user_vectors,
            axis=0,
            weights=np.asarray(weights, dtype=float)
        ))
        if user_vector is None:
            return []

        candidate_scores = {}
        if nn_model is not None and len(item_ids) >= 2:
            n_neighbors = min(max(limit * 4, limit + 5), len(item_ids))
            distances, indices = nn_model.kneighbors(
                user_vector.reshape(1, -1),
                n_neighbors=n_neighbors
            )
            for dist, idx in zip(distances[0], indices[0]):
                item_id = item_ids[idx]
                if item_id in user_item_ids:
                    continue
                candidate_scores[item_id] = max(
                    candidate_scores.get(item_id, 0.0),
                    1 - float(dist)
                )
        else:
            matrix = np.asarray(vectors, dtype=float)
            similarities = matrix @ user_vector
            for idx, score in enumerate(similarities):
                item_id = item_ids[idx]
                if item_id in user_item_ids:
                    continue
                candidate_scores[item_id] = float(score)

        scored = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)
        return [iid for iid, _ in scored[:limit]]

    @staticmethod
    def _fallback_content_recall(user_id, limit):
        """无预计算模型时的实时内容召回（轻量版）"""
        user_actions = UserAction.query.filter_by(user_id=user_id).all()
        if not user_actions:
            return []
        user_item_ids = set(a.item_id for a in user_actions)
        # 取用户交互商品的类别
        user_items = Item.query.filter(Item.id.in_(user_item_ids)).all()
        cat_ids = set(i.category_id for i in user_items if i.category_id)
        if not cat_ids:
            return []
        # 同类别商品（校园隔离）
        query = Item.query.filter(
            Item.category_id.in_(cat_ids),
            Item.status == 'on_sale',
            ~Item.id.in_(user_item_ids)
        )
        school = _get_user_school(user_id)
        school_ids = _effective_school_item_ids(user_id, school)
        if school_ids is not None:
            query = query.join(User, Item.seller_id == User.id).filter(User.school_name == school)
        candidates = query.order_by(Item.created_at.desc()).limit(limit).all()
        return [c.id for c in candidates]

    @staticmethod
    def cluster_recall(user_id, limit=CONTENT_TOPK):
        """
        语义 Embedding 聚类召回（冷启动友好）
        逻辑：商品聚类 -> 用户最近交互商品所在簇 -> 召回同簇商品
        """
        cluster_data = safe_load_model('item_clusters')
        if cluster_data is None:
            return []

        item_clusters = cluster_data.get('item_clusters', {})
        cluster_items = cluster_data.get('cluster_items', {})

        user_actions = UserAction.query.filter_by(user_id=user_id) \
            .order_by(UserAction.created_at.desc()).limit(10).all()
        if not user_actions:
            return []

        user_item_ids = set(a.item_id for a in user_actions)
        # 找到用户交互商品所在的簇
        user_clusters = Counter()
        for iid in user_item_ids:
            if iid in item_clusters:
                user_clusters[item_clusters[iid]] += 1

        if not user_clusters:
            return []

        # 从最高频簇中召回
        candidates = []
        for cluster_id, _ in user_clusters.most_common():
            for iid in cluster_items.get(cluster_id, []):
                if iid not in user_item_ids:
                    candidates.append(iid)
                if len(candidates) >= limit:
                    break
            if len(candidates) >= limit:
                break
        return candidates[:limit]

    @staticmethod
    def hot_recall(limit=HOT_TOPK, school_name=None):
        """
        热度规则召回（零行为用户兜底）
        逻辑：近3天点击/收藏最多的在售商品
        """
        three_days_ago = datetime.now() - timedelta(days=3)
        query = db.session.query(
            UserAction.item_id,
            db.func.count(UserAction.id).label('cnt')
        ).join(Item, UserAction.item_id == Item.id).filter(
            UserAction.created_at >= three_days_ago,
            UserAction.action_type.in_(['view', 'fav']),
            Item.status == 'on_sale'
        )
        # 校园隔离
        if school_name:
            query = query.join(User, Item.seller_id == User.id).filter(User.school_name == school_name)
        hot_actions = query.group_by(UserAction.item_id) \
         .order_by(db.text('cnt DESC')) \
         .limit(limit).all()

        if hot_actions:
            return [row.item_id for row in hot_actions]

        # 兜底：最新上架（校园隔离）
        fallback_query = Item.query.filter_by(status='on_sale')
        if school_name:
            fallback_query = fallback_query.join(User, Item.seller_id == User.id).filter(User.school_name == school_name)
        items = fallback_query.order_by(Item.created_at.desc()).limit(limit).all()
        return [i.id for i in items]


# ==================== 2. 排序层 ====================

class RankingEngine:
    """精排打分引擎"""

    @staticmethod
    def rank(user_id, candidate_ids):
        """
        对候选商品打分排序
        使用预训练模型或启发式打分
        """
        if not candidate_ids:
            return []

        # 尝试加载预训练排序模型
        model = safe_load_model('ranking_model')
        if model is not None:
            return RankingEngine._model_rank(user_id, candidate_ids, model)

        # 无模型时使用启发式打分
        return RankingEngine._heuristic_rank(user_id, candidate_ids)

    @staticmethod
    def _model_rank(user_id, candidate_ids, model):
        """使用 sklearn 模型打分"""
        feature_data = safe_load_model('ranking_features')
        if feature_data is None:
            return RankingEngine._heuristic_rank(user_id, candidate_ids)

        item_features = feature_data.get('item_features', {})
        scored = []
        for iid in candidate_ids:
            feat = item_features.get(iid)
            if feat is not None:
                try:
                    prob = model.predict_proba([feat])[0][1]
                    scored.append((iid, prob))
                except Exception:
                    scored.append((iid, 0.5))
            else:
                scored.append((iid, 0.5))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored

    @staticmethod
    def _heuristic_rank(user_id, candidate_ids):
        """
        启发式打分（无预训练模型时的降级方案）
        综合：热度分 + 新鲜度分 + 用户偏好匹配分
        """
        items = Item.query.filter(Item.id.in_(candidate_ids), Item.status == 'on_sale').all()
        if not items:
            return []

        # 用户偏好类别（批量预加载，避免 N+1）
        user_actions = UserAction.query.filter_by(user_id=user_id).all()
        action_item_ids = set(a.item_id for a in user_actions)
        action_items = Item.query.filter(Item.id.in_(action_item_ids)).all() if action_item_ids else []
        action_item_map = {i.id: i for i in action_items}

        cat_counter = Counter()
        for a in user_actions:
            item = action_item_map.get(a.item_id)
            if item and item.category_id:
                w = 3 if a.action_type == 'fav' else 1
                cat_counter[str(item.category_id)] += w

        top_cats = set(c for c, _ in cat_counter.most_common(5))
        now = datetime.now()

        # 批量预加载候选商品的浏览/收藏计数（避免 N+1 查询）
        candidate_item_ids = [i.id for i in items]
        view_counts = dict(
            db.session.query(UserAction.item_id, db.func.count(UserAction.id))
            .filter(UserAction.item_id.in_(candidate_item_ids), UserAction.action_type == 'view')
            .group_by(UserAction.item_id).all()
        )
        fav_counts = dict(
            db.session.query(UserAction.item_id, db.func.count(UserAction.id))
            .filter(UserAction.item_id.in_(candidate_item_ids), UserAction.action_type == 'fav')
            .group_by(UserAction.item_id).all()
        )

        scored = []
        for item in items:
            score = 0.0
            # 热度分 (0~0.4)
            views = view_counts.get(item.id, 0)
            favs = fav_counts.get(item.id, 0)
            heat = min((views + favs * 3) / 100.0, 1.0)
            score += heat * 0.4

            # 新鲜度分 (0~0.3)
            if item.created_at:
                age_hours = (now - item.created_at).total_seconds() / 3600
                freshness = max(0, 1 - age_hours / (72 * 24))  # 72天衰减到0
            else:
                freshness = 0.5
            score += freshness * 0.3

            # 类别偏好分 (0~0.3)
            if str(item.category_id) in top_cats:
                score += 0.3

            scored.append((item.id, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored


# ==================== 3. 业务重排层 ====================

class ReRankingEngine:
    """业务重排引擎：定价加权 + 时空打散"""

    @staticmethod
    def rerank(scored_items, user_id=None):
        """
        scored_items: [(item_id, score), ...]
        返回重排后的 [(item_id, final_score), ...]
        """
        if not scored_items:
            return []

        item_ids = [iid for iid, _ in scored_items]
        items = Item.query.filter(Item.id.in_(item_ids)).all()
        item_map = {i.id: i for i in items}

        # 1. 合理定价加权
        scored_items = ReRankingEngine._pricing_reweight(scored_items, item_map)

        # 2. 地点偏好加权
        if user_id:
            scored_items = ReRankingEngine._location_boost(scored_items, item_map, user_id)

        # 3. 同类打散
        scored_items = ReRankingEngine._diversity_scatter(scored_items, item_map)

        return scored_items[:FINAL_LIMIT]

    @staticmethod
    def _pricing_reweight(scored_items, item_map):
        """
        合理定价曝光加权
        KNN 找同类历史成交价 -> 价格在合理区间内提权，偏离降权
        """
        price_ref = safe_load_model('price_reference')

        reweighted = []
        for iid, score in scored_items:
            item = item_map.get(iid)
            if not item:
                continue

            if price_ref and str(item.category_id) in price_ref:
                ref = price_ref[str(item.category_id)]
                low, high = ref.get('low', 0), ref.get('high', float('inf'))
                price = float(item.price)
                if low <= price <= high:
                    score *= PRICE_BOOST
                elif price > high * 1.5 or price < low * 0.5:
                    score *= PRICE_PENALTY
            reweighted.append((iid, score))

        reweighted.sort(key=lambda x: x[1], reverse=True)
        return reweighted

    @staticmethod
    def _location_boost(scored_items, item_map, user_id):
        """地点偏好加权：用户常用交易地点的商品提权"""
        # 统计用户历史交互商品的地点（批量预加载，避免 N+1）
        user_actions = UserAction.query.filter_by(user_id=user_id).all()
        action_item_ids = set(a.item_id for a in user_actions)
        # 优先从已有 item_map 取，不足的再批量查询
        missing_ids = action_item_ids - set(item_map.keys())
        extra_items = Item.query.filter(Item.id.in_(missing_ids)).all() if missing_ids else []
        full_map = {**item_map, **{i.id: i for i in extra_items}}

        loc_counter = Counter()
        for a in user_actions:
            item = full_map.get(a.item_id)
            if item and item.location:
                loc_counter[item.location] += 1

        if not loc_counter:
            return scored_items

        top_locations = set(loc for loc, _ in loc_counter.most_common(3))
        boosted = []
        for iid, score in scored_items:
            item = item_map.get(iid)
            if item and item.location in top_locations:
                score *= 1.1
            boosted.append((iid, score))
        return boosted

    @staticmethod
    def _diversity_scatter(scored_items, item_map):
        """
        同类打散：避免推荐列表中同一类商品过多
        超过 MAX_SAME_CATEGORY 个同类商品时，多出的降权
        """
        scored_items.sort(key=lambda x: x[1], reverse=True)
        result = []
        cat_count = Counter()

        for iid, score in scored_items:
            item = item_map.get(iid)
            if not item:
                continue
            cat_key = str(item.category_id) if item.category_id else 'none'
            cat_count[cat_key] += 1
            if cat_count[cat_key] > MAX_SAME_CATEGORY:
                score *= DIVERSITY_PENALTY
            result.append((iid, score))

        result.sort(key=lambda x: x[1], reverse=True)
        return result


# ==================== 4. 推荐主入口 ====================

class RecommendationService:
    """推荐系统主服务"""

    @staticmethod
    def get_recommendations(user_id, limit=FINAL_LIMIT, refresh=False):
        """
        获取个性化推荐列表
        流程：缓存检查 -> 多路召回 -> 动态融合 -> 精排 -> 业务重排
        """
        # 1. 检查 Redis 缓存
        cache_key = f'rec:user:{user_id}'
        if redis_client and not refresh:
            try:
                cached = redis_client.get(cache_key)
                if cached:
                    item_ids = json.loads(cached)
                    items = Item.query.filter(
                        Item.id.in_(item_ids), Item.status == 'on_sale'
                    ).all()
                    item_map = {i.id: i for i in items}
                    ordered = [item_map[iid] for iid in item_ids if iid in item_map]
                    return [i.to_dict(include_seller=True) for i in ordered[:limit]]
            except Exception:
                pass

        # 校园隔离：获取用户学校
        school = _get_user_school(user_id)
        school_ids = _effective_school_item_ids(user_id, school)
        school_scope = school if school_ids is not None else None
        user_actions = UserAction.query.filter_by(user_id=user_id).all()
        action_count = len(user_actions)

        # 2. 多路召回
        recall_sources = {
            'cf': RecallEngine.collaborative_filtering_recall(user_id),
            'semantic': RecallEngine.semantic_recall(user_id),
            'content': RecallEngine.content_based_recall(user_id),
            'cluster': RecallEngine.cluster_recall(user_id),
            'hot': RecallEngine.hot_recall(school_name=school_scope),
        }
        recall_weights = _resolve_recall_weights(action_count, recall_sources)

        # 获取用户已交互的商品（用于过滤已看过的）
        user_interacted_ids = set(a.item_id for a in user_actions)

        # 3. 动态融合多路召回分数
        merged_scores = defaultdict(float)
        for source_name, item_ids in recall_sources.items():
            source_scores = _ranked_source_scores(
                item_ids[:RECALL_LIMIT],
                recall_weights.get(source_name, 0.0)
            )
            for iid, score in source_scores.items():
                if school_ids is not None and iid not in school_ids:
                    continue
                merged_scores[iid] += score

        merged = [
            iid for iid, _ in sorted(
                merged_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )[:RECALL_LIMIT]
        ]

        # 过滤掉用户自己的商品
        user = User.query.get(user_id)
        user_own_item_ids = set()
        if user:
            user_own_item_ids = set(i.id for i in user.items.all())
            merged = [iid for iid in merged if iid not in user_own_item_ids]

        # 过滤掉用户已浏览/收藏的商品（避免重复推荐）
        fresh_merged = [iid for iid in merged if iid not in user_interacted_ids]
        if len(fresh_merged) < limit:
            # 候选不足时用随机在售商品补充（校园隔离），而非回退已浏览商品
            seen_fresh = set(fresh_merged)
            exclude_ids = user_interacted_ids | seen_fresh | user_own_item_ids
            filler_query = Item.query.filter(
                Item.status == 'on_sale',
                ~Item.id.in_(exclude_ids)
            )
            if school_scope:
                filler_query = filler_query.join(User, Item.seller_id == User.id).filter(User.school_name == school)
            filler = filler_query.order_by(db.func.random()).limit(RECALL_LIMIT - len(fresh_merged)).all()
            for item in filler:
                if item.id not in seen_fresh:
                    fresh_merged.append(item.id)
                    seen_fresh.add(item.id)
                if len(fresh_merged) >= RECALL_LIMIT:
                    break
        merged = fresh_merged

        # 4. 精排打分
        scored = RankingEngine.rank(user_id, merged)

        # 5. 业务重排
        final = ReRankingEngine.rerank(scored, user_id)

        # 6. 查询商品详情并返回
        final_ids = [iid for iid, _ in final[:limit]]
        items = Item.query.filter(
            Item.id.in_(final_ids), Item.status == 'on_sale'
        ).all()
        item_map = {i.id: i for i in items}
        result = [item_map[iid].to_dict(include_seller=True)
                  for iid in final_ids if iid in item_map]

        # 7. 写入 Redis 缓存
        if redis_client and result:
            try:
                redis_client.setex(
                    cache_key, CACHE_TTL,
                    json.dumps([r['id'] for r in result])
                )
            except Exception:
                pass

        return result

    @staticmethod
    def get_similar_items(item_id, limit=10, user_id=None):
        """
        商品详情页"猜你喜欢" - 潜在语义 + TF-IDF 内容相似 + Item-CF + 同类别补充
        """
        item = Item.query.get(item_id)
        if not item:
            return []

        # 校园隔离
        school = _get_user_school(user_id)
        school_ids = _effective_school_item_ids(user_id, school)

        candidate_scores = defaultdict(float)

        # 1. 潜在语义近邻
        semantic_data = safe_load_model('semantic_index')
        if semantic_data:
            semantic_neighbors = semantic_data.get('neighbors', {})
            for neighbor_id, score in semantic_neighbors.get(item_id, [])[:limit * 3]:
                if school_ids is not None and neighbor_id not in school_ids:
                    continue
                candidate_scores[neighbor_id] += float(score) * 2.5

        # 2. TF-IDF 内容相似度
        tfidf_data = safe_load_model('tfidf_matrix')
        if tfidf_data:
            tfidf_matrix = tfidf_data.get('matrix')
            item_ids = tfidf_data.get('item_ids', [])
            item_id_to_idx = {iid: idx for idx, iid in enumerate(item_ids)}
            if item_id in item_id_to_idx:
                idx = item_id_to_idx[item_id]
                sims = cosine_similarity(
                    tfidf_matrix[idx], tfidf_matrix
                ).flatten()
                for i, score in enumerate(sims):
                    iid = item_ids[i]
                    if iid != item_id:
                        if school_ids is not None and iid not in school_ids:
                            continue
                        candidate_scores[iid] += float(score) * 1.8  # 词面相似补充

        # 3. Item-CF: 看过这个商品的人还看了什么
        viewers = UserAction.query.filter_by(
            item_id=item_id, action_type='view'
        ).all()
        viewer_ids = [v.user_id for v in viewers]
        if viewer_ids:
            other_actions = UserAction.query.filter(
                UserAction.user_id.in_(viewer_ids),
                UserAction.item_id != item_id,
                UserAction.action_type.in_(['view', 'fav'])
            ).all()
            action_count = Counter(a.item_id for a in other_actions)
            for iid, cnt in action_count.most_common(limit * 2):
                if school_ids is not None and iid not in school_ids:
                    continue
                candidate_scores[iid] += cnt * 1.0  # CF 权重

        # 4. 同类别补充（校园隔离）
        if item.category_id:
            same_cat_query = Item.query.filter(
                Item.category_id == item.category_id,
                Item.id != item_id,
                Item.status == 'on_sale'
            )
            if school:
                same_cat_query = same_cat_query.join(User, Item.seller_id == User.id).filter(User.school_name == school)
            same_cat = same_cat_query.order_by(Item.created_at.desc()).limit(limit).all()
            for i in same_cat:
                candidate_scores[i.id] += 0.5  # 同类别基础分

        # 过滤在售商品并排序
        sorted_candidates = sorted(
            candidate_scores.items(), key=lambda x: x[1], reverse=True
        )
        top_ids = [iid for iid, _ in sorted_candidates[:limit]]

        items = Item.query.filter(
            Item.id.in_(top_ids),
            Item.status == 'on_sale',
            Item.id != item_id
        ).all()
        item_map = {i.id: i for i in items}
        return [item_map[iid].to_dict(include_seller=True)
                for iid in top_ids if iid in item_map]

    @staticmethod
    def get_hot_items(limit=10, user_id=None):
        """热门商品推荐（校园隔离）"""
        school = _get_user_school(user_id)
        school_ids = _effective_school_item_ids(user_id, school)
        school_scope = school if school_ids is not None else None
        cache_key = f'rec:hot:{limit}:{school_scope or "all"}'
        try:
            if redis_client:
                cached = redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
        except Exception:
            pass

        hot_ids = RecallEngine.hot_recall(limit, school_name=school_scope)
        items = Item.query.filter(Item.id.in_(hot_ids)).all()
        item_map = {i.id: i for i in items}
        results = [item_map[iid].to_dict(include_seller=True) for iid in hot_ids if iid in item_map]
        
        try:
            if redis_client:
                redis_client.setex(cache_key, 3600, json.dumps(results))
        except Exception:
            pass
            
        return results

    @staticmethod
    def get_price_suggestion_by_category(category_id, exclude_item_id=None):
        """
        按类目提供合理定价建议
        """
        if not category_id:
            return None

        # 找同类别已成交商品
        completed_orders = db.session.query(Order, Item).join(
            Item, Order.item_id == Item.id
        ).filter(
            Item.category_id == category_id,
            Order.status == 'completed'
        ).all()

        if not completed_orders:
            # 没有成交记录，用同类在售商品价格
            query = Item.query.filter(
                Item.category_id == category_id,
                Item.status == 'on_sale'
            )
            if exclude_item_id:
                query = query.filter(Item.id != exclude_item_id)
            same_cat = query.all()
            if not same_cat:
                return None
            prices = [float(i.price) for i in same_cat]
        else:
            prices = [float(o.amount) for o, _ in completed_orders]

        if not prices:
            return None

        prices.sort()
        n = len(prices)
        return {
            'min': round(prices[0], 2),
            'max': round(prices[-1], 2),
            'avg': round(sum(prices) / n, 2),
            'median': round(prices[n // 2], 2),
            'suggested_low': round(np.percentile(prices, 25), 2),
            'suggested_high': round(np.percentile(prices, 75), 2),
            'sample_count': n
        }

    @staticmethod
    def get_price_suggestion(item_id):
        """
        合理定价建议
        KNN 找同类已成交商品的价格区间
        """
        item = Item.query.get(item_id)
        if not item:
            return None
        return RecommendationService.get_price_suggestion_by_category(
            item.category_id, exclude_item_id=item_id
        )
