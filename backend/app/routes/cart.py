from flask import Blueprint, request, jsonify
from app.models.models import CartItem, Item
from app import db
from flask_jwt_extended import jwt_required, get_jwt_identity

cart_bp = Blueprint('cart', __name__)


@cart_bp.route('/', methods=['GET'])
@jwt_required()
def get_cart():
    user_id = get_jwt_identity()
    items = CartItem.query.filter_by(user_id=user_id).order_by(CartItem.created_at.desc()).all()
    return jsonify({'items': [c.to_dict() for c in items]}), 200


@cart_bp.route('/', methods=['POST'])
@jwt_required()
def add_to_cart():
    user_id = get_jwt_identity()
    data = request.get_json()
    item_id = data.get('item_id')
    if not item_id:
        return jsonify({'msg': '商品ID不能为空'}), 400
    item = Item.query.get_or_404(item_id)
    if str(item.seller_id) == str(user_id):
        return jsonify({'msg': '不能将自己的商品加入购物车'}), 400
    if item.status != 'on_sale':
        return jsonify({'msg': '该商品已不可购买'}), 400
    # 校园隔离：验证买卖双方是否同校
    from app.models.models import User
    buyer = User.query.get(user_id)
    seller = User.query.get(item.seller_id)
    if buyer and seller and buyer.school_name and seller.school_name:
        if buyer.school_name != seller.school_name:
            return jsonify({'msg': '只能加购同校用户的商品'}), 403
    existing = CartItem.query.filter_by(user_id=user_id, item_id=item_id).first()
    if existing:
        return jsonify({'msg': '商品已在购物车中'}), 200
    cart_item = CartItem(user_id=user_id, item_id=item_id)
    db.session.add(cart_item)
    db.session.commit()
    return jsonify(cart_item.to_dict()), 201


@cart_bp.route('/<int:cart_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(cart_id):
    user_id = get_jwt_identity()
    cart_item = CartItem.query.get_or_404(cart_id)
    if str(cart_item.user_id) != str(user_id):
        return jsonify({'msg': 'Forbidden'}), 403
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'msg': '已从购物车移除'}), 200


@cart_bp.route('/clear', methods=['DELETE'])
@jwt_required()
def clear_cart():
    user_id = get_jwt_identity()
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    return jsonify({'msg': '购物车已清空'}), 200


@cart_bp.route('/batch-remove', methods=['POST'])
@jwt_required()
def batch_remove_from_cart():
    """批量移除购物车商品"""
    user_id = get_jwt_identity()
    data = request.get_json()
    cart_ids = data.get('cart_ids', [])
    if not cart_ids or not isinstance(cart_ids, list):
        return jsonify({'msg': '请选择要移除的商品'}), 400
    deleted = CartItem.query.filter(
        CartItem.id.in_(cart_ids),
        CartItem.user_id == user_id
    ).delete(synchronize_session='fetch')
    db.session.commit()
    return jsonify({'msg': f'已移除 {deleted} 件商品'}), 200


@cart_bp.route('/count', methods=['GET'])
@jwt_required()
def cart_count():
    user_id = get_jwt_identity()
    count = CartItem.query.filter_by(user_id=user_id).count()
    return jsonify({'count': count}), 200
