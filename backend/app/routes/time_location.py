"""
时空匹配API路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.time_location import TimeLocationService
from app.models.models import User, Item

time_location_bp = Blueprint('time_location', __name__, url_prefix='/api/time-location')


@time_location_bp.route('/common-locations', methods=['GET'])
def get_common_locations():
    """获取常用地点列表"""
    return jsonify(TimeLocationService.COMMON_LOCATIONS), 200


@time_location_bp.route('/time-slots', methods=['GET'])
def get_time_slots():
    """获取预定义时间段列表"""
    return jsonify(TimeLocationService.TIME_SLOTS), 200


@time_location_bp.route('/match', methods=['POST'])
@jwt_required(optional=True)
def calculate_match():
    """
    计算买卖双方的时空匹配度（未登录时返回空结果）
    """
    try:
        current_user_id = get_jwt_identity()
        # 未登录时返回空结果
        if not current_user_id:
            return jsonify({
                'match_score': 0,
                'time_match': [],
                'location_match': [],
                'suggestions': [],
                'message': '请登录后查看时空匹配信息'
            }), 200

        data = request.get_json()
        item_id = data.get('item_id')

        if not item_id:
            return jsonify({'error': 'item_id is required'}), 400

        # 获取商品信息
        item = Item.query.get(item_id)
        if not item:
            return jsonify({'error': 'Item not found'}), 404

        # 获取买家信息
        buyer = User.query.get(current_user_id)
        if not buyer:
            return jsonify({'error': 'User not found'}), 404

        # 获取卖家信息
        seller = User.query.get(item.seller_id)
        if not seller:
            return jsonify({'error': 'Seller not found'}), 404

        # 使用商品的时间地点或卖家的默认时间地点
        seller_time_slots = item.available_time_slots or seller.usual_time_slots or []
        seller_locations = item.preferred_locations or seller.usual_locations or []

        buyer_time_slots = buyer.usual_time_slots or []
        buyer_locations = buyer.usual_locations or []

        # 计算匹配建议
        suggestions = TimeLocationService.get_match_suggestions(
            buyer_time_slots, buyer_locations,
            seller_time_slots, seller_locations
        )

        return jsonify(suggestions), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@time_location_bp.route('/next-available', methods=['POST'])
def get_next_available():
    """获取下一个可用时间"""
    try:
        data = request.get_json()
        time_slots = data.get('time_slots', [])

        next_time = TimeLocationService.get_next_available_time(time_slots)

        if next_time:
            return jsonify(next_time), 200
        else:
            return jsonify({'message': 'No available time slots'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@time_location_bp.route('/validate-time-slot', methods=['POST'])
def validate_time_slot():
    """验证时间段格式"""
    try:
        data = request.get_json()
        time_slot = data.get('time_slot', '')

        is_valid = TimeLocationService.validate_time_slot(time_slot)

        return jsonify({'valid': is_valid}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
