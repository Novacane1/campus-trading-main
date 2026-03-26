from flask import Blueprint, request, jsonify
from app.models.models import Order, Item
from app import db, redis_client
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('/', methods=['POST'])
@jwt_required()
def create_order():
    user_id = get_jwt_identity()
    data = request.get_json()
    item_id = data.get('item_id')
    quantity = data.get('quantity', 1)

    if not item_id:
        return jsonify({'msg': 'Item ID is required'}), 400

    # 验证购买数量
    if quantity < 1:
        return jsonify({'msg': '购买数量必须大于0'}), 400

    # SELECT FOR UPDATE — 行级锁，防止并发超卖
    item = Item.query.filter_by(id=item_id).with_for_update().first_or_404()
    if item.status != 'on_sale':
        return jsonify({'msg': '该商品已不可购买'}), 400
    if str(item.seller_id) == str(user_id):
        return jsonify({'msg': '不能购买自己的商品'}), 400

    # 校园隔离：验证买卖双方是否同校（仅对有学校信息的用户生效）
    from app.models.models import User
    buyer = User.query.get(user_id)
    seller = User.query.get(item.seller_id)
    if buyer and seller and buyer.school_name and seller.school_name:
        if buyer.school_name != seller.school_name:
            return jsonify({'msg': '只能购买同校用户的商品'}), 403

    # 检查库存
    item_quantity = item.quantity or 1
    if quantity > item_quantity:
        return jsonify({'msg': f'库存不足，当前库存仅剩 {item_quantity} 件'}), 400

    # 计算总价
    total_amount = item.price * quantity

    now = datetime.now()
    order = Order(
        buyer_id=user_id,
        item_id=item_id,
        amount=total_amount,
        quantity=quantity,
        status='pending',
        created_at=now,
        expire_time=now + timedelta(minutes=15)
    )

    # 扣减库存
    item.quantity = item_quantity - quantity

    # 如果库存为0，标记为已售出
    if item.quantity <= 0:
        item.status = 'sold'

    db.session.add(order)
    db.session.commit()

    try:
        if redis_client:
            redis_client.hincrby('total_stats', 'total_orders', 1)
            redis_client.hincrbyfloat('total_stats', 'total_revenue', float(total_amount))
    except Exception:
        pass

    return jsonify(order.to_dict()), 201


@orders_bp.route('/batch', methods=['POST'])
@jwt_required()
def batch_create_order():
    """批量下单：接受 item_ids 列表，为每个商品创建一个订单"""
    user_id = get_jwt_identity()
    data = request.get_json()
    item_ids = data.get('item_ids', [])

    if not item_ids or not isinstance(item_ids, list):
        return jsonify({'msg': '请选择至少一个商品'}), 400
    if len(item_ids) > 50:
        return jsonify({'msg': '单次最多下单50件商品'}), 400

    orders_created = []
    errors = []

    for item_id in item_ids:
        try:
            item = Item.query.filter_by(id=item_id).with_for_update().first()
            if not item:
                errors.append({'item_id': item_id, 'msg': '商品不存在'})
                continue
            if item.status != 'on_sale':
                errors.append({'item_id': item_id, 'msg': f'"{item.name}" 已不可购买'})
                continue
            if str(item.seller_id) == str(user_id):
                errors.append({'item_id': item_id, 'msg': f'不能购买自己的商品 "{item.name}"'})
                continue

            now = datetime.now()
            order = Order(
                buyer_id=user_id,
                item_id=item_id,
                amount=item.price,
                status='pending',
                created_at=now,
                expire_time=now + timedelta(minutes=15)
            )
            item.status = 'sold'
            db.session.add(order)
            orders_created.append(order)
        except Exception as e:
            errors.append({'item_id': item_id, 'msg': str(e)})

    if not orders_created and errors:
        db.session.rollback()
        return jsonify({'msg': errors[0]['msg'], 'errors': errors}), 400

    db.session.commit()

    try:
        if redis_client:
            redis_client.hincrby('total_stats', 'total_orders', len(orders_created))
            total_revenue = sum(float(o.amount) for o in orders_created)
            redis_client.hincrbyfloat('total_stats', 'total_revenue', total_revenue)
    except Exception:
        pass

    return jsonify({
        'msg': f'成功下单 {len(orders_created)} 件商品',
        'orders': [o.to_dict() for o in orders_created],
        'errors': errors
    }), 201


@orders_bp.route('/me', methods=['GET'])
@jwt_required()
def get_my_orders():
    user_id = get_jwt_identity()
    status = request.args.get('status')
    query = Order.query.filter_by(buyer_id=user_id)
    if status:
        query = query.filter_by(status=status)
    orders = query.order_by(Order.created_at.desc()).all()
    return jsonify({'orders': [o.to_dict() for o in orders]}), 200


@orders_bp.route('/sales', methods=['GET'])
@jwt_required()
def get_my_sales():
    user_id = int(get_jwt_identity())
    status = request.args.get('status')
    # Find orders for items where current user is the seller
    query = Order.query.join(Item).filter(Item.seller_id == user_id)
    if status:
        query = query.filter(Order.status == status)
    orders = query.order_by(Order.created_at.desc()).all()
    return jsonify({'orders': [o.to_dict() for o in orders]}), 200


@orders_bp.route('/<string:order_id>', methods=['GET'])
@jwt_required()
def get_order_detail(order_id):
    user_id = int(get_jwt_identity())
    order = Order.query.get_or_404(order_id)
    item = Item.query.get(order.item_id)
    if order.buyer_id != user_id and (not item or item.seller_id != user_id):
        return jsonify({'msg': 'Forbidden'}), 403
    return jsonify(order.to_dict()), 200


@orders_bp.route('/<string:order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    user_id = int(get_jwt_identity())
    order = Order.query.get_or_404(order_id)
    item = Item.query.get(order.item_id)
    if order.buyer_id != user_id and (not item or item.seller_id != user_id):
        return jsonify({'msg': 'Forbidden'}), 403
    data = request.get_json()
    new_status = data.get('status')
    valid = ['pending', 'paid', 'shipped', 'completed', 'cancelled']
    if new_status not in valid:
        return jsonify({'msg': f'无效状态，可选: {valid}'}), 400
    if new_status == 'cancelled' and order.status not in ('pending', 'paid'):
        return jsonify({'msg': '当前状态不可取消'}), 400
    order.status = new_status
    if new_status == 'cancelled':
        if item:
            item.status = 'on_sale'
    db.session.commit()
    return jsonify(order.to_dict()), 200


@orders_bp.route('/<string:order_id>/confirm', methods=['PUT'])
@jwt_required()
def confirm_order(order_id):
    user_id = int(get_jwt_identity())
    order = Order.query.get_or_404(order_id)
    if order.buyer_id != user_id:
        return jsonify({'msg': '只有买家可以确认收货'}), 403
    order.status = 'completed'
    db.session.commit()
    return jsonify(order.to_dict()), 200
