"""
推荐系统 API 路由
提供：个性化推荐、相似商品、定价建议
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.recommendation import RecommendationService

recommendations_bp = Blueprint('recommendations', __name__)


@recommendations_bp.route('/personal', methods=['GET'])
@jwt_required()
def get_personal_recommendations():
    """个性化推荐（首页"猜你喜欢"）"""
    user_id = get_jwt_identity()
    limit = request.args.get('limit', 20, type=int)
    force_refresh = str(request.args.get('force_refresh', '')).lower() in ('1', 'true', 'yes')
    try:
        results = RecommendationService.get_recommendations(user_id, limit, refresh=force_refresh)
        return jsonify({'items': results, 'products': results, 'source': 'recommendation'}), 200
    except Exception as e:
        print(f'推荐服务异常: {e}')
        return jsonify({'items': [], 'products': [], 'source': 'fallback', 'error': str(e)}), 200


@recommendations_bp.route('/similar/<int:item_id>', methods=['GET'])
@jwt_required(optional=True)
def get_similar_items(item_id):
    """相似商品推荐（商品详情页"猜你喜欢"）"""
    user_id = get_jwt_identity()
    limit = request.args.get('limit', 10, type=int)
    try:
        results = RecommendationService.get_similar_items(item_id, limit, user_id=user_id)
        return jsonify({'items': results, 'products': results}), 200
    except Exception as e:
        print(f'相似推荐异常: {e}')
        return jsonify({'items': [], 'products': []}), 200


@recommendations_bp.route('/price-suggestion/<int:item_id>', methods=['GET'])
def get_price_suggestion(item_id):
    """合理定价建议"""
    try:
        result = RecommendationService.get_price_suggestion(item_id)
        if result:
            return jsonify({
                'average_price': result['avg'],
                'median_price': result['median'],
                'min_price': result['min'],
                'max_price': result['max'],
                **result
            }), 200
        return jsonify({'msg': '暂无定价参考数据'}), 404
    except Exception as e:
        print(f'定价建议异常: {e}')
        return jsonify({'msg': str(e)}), 500

@recommendations_bp.route('/price-suggestion', methods=['GET'])
def get_price_suggestion_by_category():
    """合理定价建议 (按类目)"""
    category_id = request.args.get('category_id')
    try:
        result = RecommendationService.get_price_suggestion_by_category(category_id)
        if result:
            return jsonify({
                'average_price': result['avg'],
                'median_price': result['median'],
                'min_price': result['min'],
                'max_price': result['max'],
                **result
            }), 200
        return jsonify({'msg': '暂无定价参考数据'}), 404
    except Exception as e:
        print(f'定价建议异常: {e}')
        return jsonify({'msg': str(e)}), 500

@recommendations_bp.route('/hot', methods=['GET'])
@jwt_required(optional=True)
def get_hot_items():
    """热门商品推荐"""
    user_id = get_jwt_identity()
    limit = request.args.get('limit', 30, type=int)
    try:
        results = RecommendationService.get_hot_items(limit, user_id=user_id)
        return jsonify({'items': results, 'products': results}), 200
    except Exception as e:
        print(f'热门推荐异常: {e}')
        return jsonify({'items': [], 'products': []}), 500
