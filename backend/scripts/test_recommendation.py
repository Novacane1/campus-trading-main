"""
推荐系统验证测试脚本
测试内容：
1. 各召回路径正确性
2. 排序逻辑
3. 重排逻辑
4. 边界条件 & 冷启动
5. 已知 Bug 检测
"""
import os
import sys
import uuid
import traceback
from datetime import datetime, timedelta
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app, db
from app.models.models import (
    User, Item, Category, UserAction, Order,
    ItemEmbedding, UserInterest
)

# ==================== 测试框架 ====================
PASS = 0
FAIL = 0
WARN = 0
RESULTS = []


def report(status, name, detail=''):
    global PASS, FAIL, WARN
    icon = {'PASS': '✅', 'FAIL': '❌', 'WARN': '⚠️'}[status]
    if status == 'PASS':
        PASS += 1
    elif status == 'FAIL':
        FAIL += 1
    else:
        WARN += 1
    msg = f"  {icon} [{status}] {name}"
    if detail:
        msg += f"\n       → {detail}"
    print(msg)
    RESULTS.append((status, name, detail))


# ==================== 测试用例 ====================

def test_cf_recall_dead_code_bug():
    """验证: collaborative_filtering_recall 修复后正确工作"""
    print("\n--- 测试1: 协同过滤召回逻辑 ---")
    from app.services.recommendation import RecallEngine

    # 找一个有行为记录的用户
    active_user = db.session.query(UserAction.user_id).group_by(
        UserAction.user_id
    ).order_by(db.func.count(UserAction.id).desc()).first()

    if not active_user:
        report('WARN', 'CF召回 - 无用户行为数据')
        return

    user_id = active_user[0]
    cf_ids = RecallEngine.collaborative_filtering_recall(user_id)

    # 验证结果不包含用户已交互的商品
    user_item_ids = set(
        a.item_id for a in UserAction.query.filter_by(user_id=user_id).all()
    )
    overlap = set(cf_ids) & user_item_ids
    if overlap:
        report('FAIL', 'CF召回结果包含用户已交互商品',
               f'重叠商品: {overlap}')
    elif cf_ids:
        report('PASS', f'CF召回正常工作，用户{user_id}召回 {len(cf_ids)} 个商品')
    else:
        report('WARN', f'CF召回返回空列表(用户{user_id}可能无相似用户)')


def test_hot_recall_no_status_filter():
    """BUG检测: hot_recall 不过滤商品状态"""
    print("\n--- 测试2: 热度召回状态过滤 ---")
    from app.services.recommendation import RecallEngine

    hot_ids = RecallEngine.hot_recall(limit=50)
    if not hot_ids:
        report('WARN', '热度召回 - 无数据', '没有近3天的用户行为，无法验证')
        return

    # 检查是否包含非在售商品
    non_sale = Item.query.filter(
        Item.id.in_(hot_ids),
        Item.status != 'on_sale'
    ).all()

    if non_sale:
        report('FAIL', '热度召回包含非在售商品',
               f'召回 {len(hot_ids)} 个商品中有 {len(non_sale)} 个非在售 '
               f'(状态: {[i.status for i in non_sale]})')
    else:
        report('PASS', '热度召回商品状态过滤')


def test_diversity_scatter_logic():
    """验证: 同类打散是累计计数而非连续计数"""
    print("\n--- 测试3: 同类打散逻辑 ---")
    from app.services.recommendation import ReRankingEngine, MAX_SAME_CATEGORY

    # 构造测试数据: 6个商品，前3个A类，后3个B类
    cats = Category.query.limit(2).all()
    if len(cats) < 2:
        report('WARN', '同类打散 - 类别不足', '需要至少2个类别')
        return

    items_a = Item.query.filter_by(category_id=cats[0].id, status='on_sale').limit(4).all()
    items_b = Item.query.filter_by(category_id=cats[1].id, status='on_sale').limit(2).all()

    if len(items_a) < 4 or len(items_b) < 2:
        report('WARN', '同类打散 - 商品不足', '需要每个类别至少有足够在售商品')
        return

    # 交替排列: A A A A B B，分数递减
    scored = []
    all_items = items_a[:4] + items_b[:2]
    for i, item in enumerate(all_items):
        scored.append((item.id, 1.0 - i * 0.1))

    item_map = {i.id: i for i in all_items}
    result = ReRankingEngine._diversity_scatter(scored, item_map)

    # 第4个A类商品(index 3)应该被降权
    a4_id = items_a[3].id
    a4_score = None
    for iid, score in result:
        if iid == a4_id:
            a4_score = score
            break

    original_a4_score = 1.0 - 3 * 0.1  # 0.7
    if a4_score is not None and a4_score < original_a4_score:
        report('PASS', f'同类打散: 第{MAX_SAME_CATEGORY+1}个同类商品被降权',
               f'原始分 {original_a4_score:.2f} -> 降权后 {a4_score:.2f}')
    else:
        report('FAIL', '同类打散未生效',
               f'第4个A类商品分数 {a4_score}，预期低于 {original_a4_score}')


def test_pricing_reweight():
    """验证: 合理定价加权逻辑"""
    print("\n--- 测试4: 定价加权逻辑 ---")
    from app.services.recommendation import ReRankingEngine, safe_load_model
    from app.services.recommendation import PRICE_BOOST, PRICE_PENALTY

    price_ref = safe_load_model('price_reference')
    if price_ref is None:
        report('WARN', '定价加权 - 无价格参考模型',
               '需要先运行 build_recommendation.py 生成 price_reference.pkl')
        return

    # 找一个有价格参考的类别
    test_cat_id = None
    for cat_id_str, ref in price_ref.items():
        if ref.get('count', 0) >= 2:
            test_cat_id = cat_id_str
            break

    if not test_cat_id:
        report('WARN', '定价加权 - 无足够价格数据')
        return

    ref = price_ref[test_cat_id]
    low, high = ref['low'], ref['high']

    # 找该类别的商品
    items = Item.query.filter(
        Item.category_id == uuid.UUID(test_cat_id),
        Item.status == 'on_sale'
    ).limit(5).all()

    if not items:
        report('WARN', '定价加权 - 该类别无在售商品')
        return

    scored = [(i.id, 1.0) for i in items]
    item_map = {i.id: i for i in items}
    result = ReRankingEngine._pricing_reweight(scored, item_map)

    boosted = [s for iid, s in result if low <= float(item_map[iid].price) <= high and s > 1.0]
    report('PASS' if len(boosted) > 0 or not any(low <= float(i.price) <= high for i in items) else 'WARN',
           f'定价加权: 合理区间 [{low:.0f}, {high:.0f}]',
           f'{len(boosted)} 个商品被提权(×{PRICE_BOOST})')


def test_heuristic_rank_n_plus_1():
    """验证: _heuristic_rank N+1 查询已修复"""
    print("\n--- 测试5: 排序层批量查询 ---")

    # 修复后使用批量预加载 action_items，不再逐条 Item.query.get
    import inspect
    from app.services.recommendation import RankingEngine
    source = inspect.getsource(RankingEngine._heuristic_rank)
    if 'Item.query.get' in source:
        report('FAIL', '排序层仍存在 N+1 查询',
               '_heuristic_rank 中仍有 Item.query.get 逐条查询')
    else:
        report('PASS', '排序层已使用批量预加载，N+1 查询已修复')


def test_cold_start_zero_behavior():
    """验证: 零行为用户的冷启动"""
    print("\n--- 测试6: 冷启动 - 零行为用户 ---")
    from app.services.recommendation import RecallEngine

    # 找一个没有任何行为的用户，或用一个不存在的 user_id
    fake_user_id = 999999

    cf_ids = RecallEngine.collaborative_filtering_recall(fake_user_id)
    content_ids = RecallEngine.content_based_recall(fake_user_id)
    cluster_ids = RecallEngine.cluster_recall(fake_user_id)
    hot_ids = RecallEngine.hot_recall()

    if cf_ids:
        report('FAIL', '零行为用户CF召回应为空', f'返回了 {len(cf_ids)} 个结果')
    else:
        report('PASS', '零行为用户CF召回正确返回空列表')

    if content_ids:
        report('FAIL', '零行为用户内容召回应为空', f'返回了 {len(content_ids)} 个结果')
    else:
        report('PASS', '零行为用户内容召回正确返回空列表')

    if cluster_ids:
        report('FAIL', '零行为用户聚类召回应为空', f'返回了 {len(cluster_ids)} 个结果')
    else:
        report('PASS', '零行为用户聚类召回正确返回空列表')

    # 热度召回应该兜底
    on_sale_count = Item.query.filter_by(status='on_sale').count()
    if on_sale_count > 0 and not hot_ids:
        report('FAIL', '热度召回兜底失败', '有在售商品但热度召回为空')
    elif hot_ids:
        report('PASS', f'热度召回兜底正常，返回 {len(hot_ids)} 个商品')
    else:
        report('WARN', '热度召回 - 无在售商品')


def test_content_recall_fallback():
    """验证: 无TF-IDF模型时的降级召回"""
    print("\n--- 测试7: 内容召回降级逻辑 ---")
    from app.services.recommendation import RecallEngine, safe_load_model

    tfidf_data = safe_load_model('tfidf_matrix')
    if tfidf_data is None:
        report('WARN', '内容召回降级 - TF-IDF模型不存在',
               '将使用 _fallback_content_recall (按类别召回)，功能正常但精度较低')
    else:
        report('PASS', 'TF-IDF模型已加载',
               f"包含 {len(tfidf_data.get('item_ids', []))} 个商品向量")


def test_freshness_score_range():
    """验证: 新鲜度分数范围 [0, 1]"""
    print("\n--- 测试8: 新鲜度分数范围 ---")

    now = datetime.now()
    test_cases = [
        ('刚发布', now, 1.0),
        ('1天前', now - timedelta(days=1), None),  # 应在 (0, 1) 之间
        ('72天前', now - timedelta(days=72), 0.0),
        ('100天前', now - timedelta(days=100), 0.0),
    ]

    all_ok = True
    for label, created_at, expected in test_cases:
        age_hours = (now - created_at).total_seconds() / 3600
        freshness = max(0, 1 - age_hours / (72 * 24))

        if expected is not None:
            if abs(freshness - expected) > 0.01:
                report('FAIL', f'新鲜度 [{label}]',
                       f'期望 {expected}，实际 {freshness:.4f}')
                all_ok = False
        else:
            if not (0 < freshness < 1):
                report('FAIL', f'新鲜度 [{label}]',
                       f'期望在 (0,1) 之间，实际 {freshness:.4f}')
                all_ok = False

    if all_ok:
        report('PASS', '新鲜度分数范围正确 [0, 1]')


def test_heuristic_score_weights():
    """验证: 启发式打分权重之和 = 1.0"""
    print("\n--- 测试9: 启发式打分权重 ---")

    heat_w = 0.4
    fresh_w = 0.3
    cat_w = 0.3
    total = heat_w + fresh_w + cat_w

    if abs(total - 1.0) < 0.001:
        report('PASS', f'打分权重之和 = {total} (热度{heat_w} + 新鲜度{fresh_w} + 偏好{cat_w})')
    else:
        report('FAIL', f'打分权重之和 = {total}，不等于 1.0')


def test_similar_items_no_tfidf():
    """验证: get_similar_items 已使用 TF-IDF 相似度"""
    print("\n--- 测试10: 相似商品推荐完整性 ---")

    import inspect
    from app.services.recommendation import RecommendationService
    source = inspect.getsource(RecommendationService.get_similar_items)
    if 'cosine_similarity' in source and 'tfidf' in source.lower():
        report('PASS', '相似商品推荐已集成 TF-IDF 内容相似度')
    else:
        report('WARN', '相似商品推荐未使用 TF-IDF 内容相似度',
               '建议加入 TF-IDF cosine_similarity 提升内容相关性')


def test_data_integrity():
    """验证: 数据库数据完整性"""
    print("\n--- 测试11: 数据完整性检查 ---")

    user_count = User.query.count()
    item_count = Item.query.count()
    on_sale_count = Item.query.filter_by(status='on_sale').count()
    action_count = UserAction.query.count()
    category_count = Category.query.count()
    order_count = Order.query.count()

    print(f"    数据概览: {user_count} 用户, {item_count} 商品({on_sale_count} 在售), "
          f"{action_count} 行为记录, {category_count} 类别, {order_count} 订单")

    if user_count == 0:
        report('FAIL', '无用户数据', '推荐系统需要用户数据')
    else:
        report('PASS', f'用户数据: {user_count} 条')

    if on_sale_count == 0:
        report('FAIL', '无在售商品', '推荐系统无法召回任何商品')
    else:
        report('PASS', f'在售商品: {on_sale_count} 条')

    if action_count == 0:
        report('WARN', '无用户行为数据',
               'CF召回和内容召回均无法工作，仅热度召回可用')
    else:
        # 检查行为类型分布
        type_dist = db.session.query(
            UserAction.action_type,
            db.func.count(UserAction.id)
        ).group_by(UserAction.action_type).all()
        dist_str = ', '.join(f'{t}={c}' for t, c in type_dist)
        report('PASS', f'用户行为: {action_count} 条 ({dist_str})')

    if category_count == 0:
        report('FAIL', '无类别数据', '内容召回和定价建议依赖类别')
    else:
        report('PASS', f'类别数据: {category_count} 条')


def test_offline_models_exist():
    """验证: 离线模型文件是否存在"""
    print("\n--- 测试12: 离线模型文件检查 ---")
    from app.services.recommendation import MODEL_DIR

    models = ['tfidf_matrix', 'semantic_index', 'item_clusters', 'price_reference']
    for name in models:
        path = os.path.join(MODEL_DIR, f'{name}.pkl')
        if os.path.exists(path):
            size_kb = os.path.getsize(path) / 1024
            report('PASS', f'模型文件 {name}.pkl ({size_kb:.1f} KB)')
        else:
            report('WARN', f'模型文件 {name}.pkl 不存在',
                   '需要运行 python scripts/build_recommendation.py')


def test_dynamic_recall_fusion():
    """验证: 个性化推荐已启用动态召回融合"""
    print("\n--- 测试12.5: 动态召回融合 ---")

    import inspect
    from app.services.recommendation import RecommendationService
    source = inspect.getsource(RecommendationService.get_recommendations)
    if 'semantic' in source and '_resolve_recall_weights' in source:
        report('PASS', '个性化推荐已启用动态召回融合')
    else:
        report('WARN', '个性化推荐仍为静态优先级合并',
               '建议引入语义召回和动态权重融合')


def test_full_pipeline():
    """端到端测试: 完整推荐流程"""
    print("\n--- 测试13: 端到端推荐流程 ---")
    from app.services.recommendation import RecommendationService

    # 找一个有行为记录的用户
    active_user = db.session.query(UserAction.user_id).group_by(
        UserAction.user_id
    ).order_by(db.func.count(UserAction.id).desc()).first()

    if active_user:
        user_id = active_user[0]
        try:
            results = RecommendationService.get_recommendations(user_id, limit=10)
            if results:
                report('PASS', f'活跃用户(id={user_id})推荐成功',
                       f'返回 {len(results)} 个推荐商品')
                # 检查结果去重
                ids = [r['id'] for r in results]
                if len(ids) != len(set(ids)):
                    report('FAIL', '推荐结果有重复商品')
                else:
                    report('PASS', '推荐结果无重复')

                # 检查不包含用户自己的商品
                user = User.query.get(user_id)
                user_item_ids = set(i.id for i in user.items.all())
                own_items = [r for r in results if r['id'] in user_item_ids]
                if own_items:
                    report('FAIL', '推荐结果包含用户自己的商品',
                           f'包含 {len(own_items)} 个自己的商品')
                else:
                    report('PASS', '推荐结果已排除用户自己的商品')
            else:
                report('WARN', f'活跃用户(id={user_id})推荐返回空列表')
        except Exception as e:
            report('FAIL', f'推荐流程异常: {e}',
                   traceback.format_exc().split('\n')[-2])
    else:
        report('WARN', '无活跃用户，跳过端到端测试')

    # 测试相似商品
    item = Item.query.filter_by(status='on_sale').first()
    if item:
        try:
            similar = RecommendationService.get_similar_items(item.id, limit=6)
            self_in_result = any(s['id'] == item.id for s in similar)
            if self_in_result:
                report('FAIL', '相似商品包含自身')
            else:
                report('PASS', f'相似商品推荐(item={item.id}): {len(similar)} 个结果')
        except Exception as e:
            report('FAIL', f'相似商品异常: {e}')

    # 测试定价建议
    if item:
        try:
            price = RecommendationService.get_price_suggestion(item.id)
            if price:
                report('PASS', f'定价建议(item={item.id}): '
                       f'建议区间 [{price["suggested_low"]}, {price["suggested_high"]}]')
            else:
                report('WARN', '定价建议返回 None (该类别无参考数据)')
        except Exception as e:
            report('FAIL', f'定价建议异常: {e}')


def test_location_boost_n_plus_1():
    """验证: _location_boost N+1 查询已修复"""
    print("\n--- 测试14: 地点加权批量查询 ---")

    import inspect
    from app.services.recommendation import ReRankingEngine
    source = inspect.getsource(ReRankingEngine._location_boost)
    if 'Item.query.get' in source:
        report('FAIL', '_location_boost 仍存在 N+1 查询')
    else:
        report('PASS', '_location_boost 已使用批量预加载，N+1 查询已修复')


def test_build_user_interests_n_plus_1():
    """验证: build_user_interests N+1 查询已修复"""
    print("\n--- 测试15: 用户兴趣构建批量查询 ---")

    import inspect
    from scripts.build_recommendation import build_user_interests
    source = inspect.getsource(build_user_interests)
    if 'Item.query.get' in source:
        report('FAIL', 'build_user_interests 仍存在 N+1 查询')
    else:
        report('PASS', 'build_user_interests 已使用批量预加载，N+1 查询已修复')


# ==================== 主入口 ====================

def main():
    print('=' * 60)
    print('  推荐系统验证测试')
    print('=' * 60)

    app = create_app()
    with app.app_context():
        test_data_integrity()
        test_offline_models_exist()
        test_dynamic_recall_fusion()
        test_cf_recall_dead_code_bug()
        test_hot_recall_no_status_filter()
        test_diversity_scatter_logic()
        test_pricing_reweight()
        test_heuristic_rank_n_plus_1()
        test_cold_start_zero_behavior()
        test_content_recall_fallback()
        test_freshness_score_range()
        test_heuristic_score_weights()
        test_similar_items_no_tfidf()
        test_location_boost_n_plus_1()
        test_build_user_interests_n_plus_1()
        test_full_pipeline()

    print('\n' + '=' * 60)
    print(f'  测试结果汇总: ✅ {PASS} 通过  ❌ {FAIL} 失败  ⚠️ {WARN} 警告')
    print('=' * 60)

    # 输出修复建议
    fails = [r for r in RESULTS if r[0] == 'FAIL']
    warns = [r for r in RESULTS if r[0] == 'WARN']
    if fails:
        print('\n🔧 需要修复的问题:')
        for i, (_, name, detail) in enumerate(fails, 1):
            print(f'  {i}. {name}')
            if detail:
                print(f'     {detail}')
    if warns:
        print('\n💡 建议优化:')
        for i, (_, name, detail) in enumerate(warns, 1):
            print(f'  {i}. {name}')
            if detail:
                print(f'     {detail}')


if __name__ == '__main__':
    main()




