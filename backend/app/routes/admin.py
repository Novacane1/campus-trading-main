from flask import Blueprint, request, jsonify
from app.models.models import (
    User, Item, Order, SystemLog, Category, Application, Location,
    Review, Announcement, Report, Appeal, Banner
)
from app import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, desc
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)


def require_admin():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.student_id != 'admin':
        return None
    return user


def log_admin_action(user_id, module, action, detail='', ip=''):
    log = SystemLog(
        level='info', module=module, action=action,
        detail=detail, user_id=user_id, ip_address=ip
    )
    db.session.add(log)
    db.session.commit()


@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    total_users = User.query.count()
    total_items = Item.query.filter(Item.status != 'deleted').count()
    total_orders = Order.query.count()
    revenue = db.session.query(func.sum(Order.amount)).scalar() or 0
    pending_items = Item.query.filter_by(status='locked').count()
    return jsonify({
        'total_users': total_users,
        'total_items': total_items,
        'total_orders': total_orders,
        'total_revenue': float(revenue),
        'pending_items': pending_items
    }), 200


@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    search = request.args.get('search', '')
    query = User.query
    if search:
        query = query.filter(
            db.or_(
                User.username.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%'),
                User.student_id.ilike(f'%{search}%')
            )
        )
    total = query.count()
    users = query.order_by(desc(User.id)).offset((page - 1) * limit).limit(limit).all()
    return jsonify({'users': [u.to_dict() for u in users], 'total': total}), 200


@admin_bp.route('/users/<int:uid>', methods=['PUT'])
@jwt_required()
def update_user(uid):
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    user = User.query.get_or_404(uid)
    data = request.get_json()
    if 'credit_score' in data:
        user.credit_score = data['credit_score']
    if 'school_name' in data:
        user.school_name = data['school_name']
    if 'can_publish' in data:
        user.can_publish = data['can_publish']
    db.session.commit()
    log_admin_action(admin.id, '用户管理', f'更新用户 {user.username}',
                     str(data), request.remote_addr)
    return jsonify(user.to_dict()), 200


@admin_bp.route('/users/<int:uid>', methods=['DELETE'])
@jwt_required()
def delete_user(uid):
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    user = User.query.get_or_404(uid)
    user.credit_score = 0
    db.session.commit()
    log_admin_action(admin.id, '用户管理', f'禁用用户 {user.username}',
                     '', request.remote_addr)
    return jsonify({'msg': '用户已禁用'}), 200


@admin_bp.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    query = Item.query
    if search:
        query = query.filter(Item.name.ilike(f'%{search}%'))
    if status:
        query = query.filter_by(status=status)
    total = query.count()
    items = query.order_by(desc(Item.created_at)).offset((page - 1) * limit).limit(limit).all()
    return jsonify({
        'products': [i.to_dict(include_seller=True) for i in items],
        'total': total
    }), 200


@admin_bp.route('/products/<int:item_id>/approve', methods=['PUT'])
@jwt_required()
def approve_product(item_id):
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    item = Item.query.get_or_404(item_id)
    item.status = 'on_sale'
    db.session.commit()
    log_admin_action(admin.id, '商品管理', f'审核通过商品 {item.name}',
                     '', request.remote_addr)
    return jsonify(item.to_dict()), 200


@admin_bp.route('/products/<int:item_id>/reject', methods=['PUT'])
@jwt_required()
def reject_product(item_id):
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    item = Item.query.get_or_404(item_id)
    data = request.get_json() or {}
    item.status = 'deleted'
    db.session.commit()
    log_admin_action(admin.id, '商品管理', f'下架商品 {item.name}',
                     data.get('reason', ''), request.remote_addr)
    return jsonify({'msg': '商品已下架'}), 200


@admin_bp.route('/products/<int:item_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_product(item_id):
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    item = Item.query.get_or_404(item_id)
    item.status = 'deleted'
    db.session.commit()
    log_admin_action(admin.id, '商品管理', f'删除商品 {item.name}',
                     '', request.remote_addr)
    return jsonify({'msg': '商品已删除'}), 200


@admin_bp.route('/logs', methods=['GET'])
@jwt_required()
def get_logs():
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    level = request.args.get('level', '')
    query = SystemLog.query
    if level:
        query = query.filter_by(level=level)
    total = query.count()
    logs = query.order_by(desc(SystemLog.created_at)).offset((page - 1) * limit).limit(limit).all()
    return jsonify({'logs': [l.to_dict() for l in logs], 'total': total}), 200


@admin_bp.route('/categories', methods=['POST'])
@jwt_required()
def admin_create_category():
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({'msg': '分类名称不能为空'}), 400
    if Category.query.filter_by(name=name).first():
        return jsonify({'msg': '分类已存在'}), 400
    cat = Category(name=name, parent_id=data.get('parent_id'),
                   icon=data.get('icon'), sort_order=data.get('sort_order', 0))
    db.session.add(cat)
    db.session.commit()
    log_admin_action(admin.id, '分类管理', f'创建分类 {name}',
                     '', request.remote_addr)
    return jsonify(cat.to_dict()), 201


@admin_bp.route('/categories/<string:cat_id>', methods=['PUT'])
@jwt_required()
def admin_update_category(cat_id):
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    cat = Category.query.get_or_404(cat_id)
    data = request.get_json()
    if 'name' in data:
        cat.name = data['name']
    if 'icon' in data:
        cat.icon = data['icon']
    if 'sort_order' in data:
        cat.sort_order = data['sort_order']
    db.session.commit()
    return jsonify(cat.to_dict()), 200


@admin_bp.route('/categories/<string:cat_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_category(cat_id):
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    cat = Category.query.get_or_404(cat_id)
    if cat.items.count() > 0:
        return jsonify({'msg': '该分类下有商品，无法删除'}), 400
    db.session.delete(cat)
    db.session.commit()
    log_admin_action(admin.id, '分类管理', f'删除分类 {cat.name}',
                     '', request.remote_addr)
    return jsonify({'msg': '分类已删除'}), 200


@admin_bp.route('/applications', methods=['GET'])
@jwt_required()
def get_applications():
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    status = request.args.get('status', '')
    app_type = request.args.get('type', '')
    query = Application.query
    if status:
        query = query.filter_by(status=status)
    if app_type:
        query = query.filter_by(app_type=app_type)
    total = query.count()
    apps = query.order_by(desc(Application.created_at)).offset((page - 1) * limit).limit(limit).all()
    return jsonify({'applications': [a.to_dict() for a in apps], 'total': total}), 200


@admin_bp.route('/applications/<int:app_id>/approve', methods=['PUT'])
@jwt_required()
def approve_application(app_id):
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    app = Application.query.get_or_404(app_id)
    if app.status != 'pending':
        return jsonify({'msg': '该申请已处理'}), 400
    app.status = 'approved'
    if app.app_type == 'category':
        if not Category.query.filter_by(name=app.name).first():
            cat = Category(name=app.name)
            db.session.add(cat)
    elif app.app_type == 'location':
        if not Location.query.filter_by(name=app.name).first():
            loc = Location(name=app.name, description=app.description or '')
            db.session.add(loc)
    db.session.commit()
    log_admin_action(admin.id, '审核管理', f'通过{app.app_type}申请: {app.name}',
                     '', request.remote_addr)
    return jsonify(app.to_dict()), 200


@admin_bp.route('/applications/<int:app_id>/reject', methods=['PUT'])
@jwt_required()
def reject_application(app_id):
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    app = Application.query.get_or_404(app_id)
    if app.status != 'pending':
        return jsonify({'msg': '该申请已处理'}), 400
    data = request.get_json() or {}
    app.status = 'rejected'
    app.reject_reason = data.get('reason', '')
    db.session.commit()
    log_admin_action(admin.id, '审核管理', f'拒绝{app.app_type}申请: {app.name}',
                     app.reject_reason, request.remote_addr)
    return jsonify(app.to_dict()), 200


@admin_bp.route('/users/<int:uid>/toggle-publish', methods=['PUT'])
@jwt_required()
def toggle_publish(uid):
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    user = User.query.get_or_404(uid)
    data = request.get_json() or {}
    user.can_publish = data.get('can_publish', not user.can_publish)
    db.session.commit()
    status_text = '允许' if user.can_publish else '禁止'
    log_admin_action(admin.id, '用户管理', f'{status_text}用户 {user.username} 发布商品',
                     '', request.remote_addr)
    return jsonify(user.to_dict()), 200


# ==================== 订单管理 ====================

@admin_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    """获取所有订单列表"""
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    status = request.args.get('status', '')
    search = request.args.get('search', '')
    is_abnormal = request.args.get('abnormal', '', type=str)

    query = Order.query
    if status:
        query = query.filter_by(status=status)
    if search:
        query = query.join(Item).filter(Item.name.ilike(f'%{search}%'))

    # 筛选异常订单：超时未支付、长时间未发货等
    if is_abnormal == 'true':
        now = datetime.now()
        query = query.filter(
            db.or_(
                # 超时未支付
                db.and_(Order.status == 'pending', Order.expire_time < now),
                # 已支付超过3天未发货
                db.and_(Order.status == 'paid', Order.created_at < now - timedelta(days=3)),
                # 已发货超过7天未确认
                db.and_(Order.status == 'shipped', Order.created_at < now - timedelta(days=7))
            )
        )

    total = query.count()
    orders = query.order_by(desc(Order.created_at)).offset((page - 1) * limit).limit(limit).all()
    return jsonify({'orders': [o.to_dict() for o in orders], 'total': total}), 200


@admin_bp.route('/orders/<string:order_id>', methods=['GET'])
@jwt_required()
def get_order_detail(order_id):
    """获取订单详情"""
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    order = Order.query.get_or_404(order_id)
    return jsonify(order.to_dict()), 200


@admin_bp.route('/orders/<string:order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    """管理员更新订单状态"""
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    order = Order.query.get_or_404(order_id)
    data = request.get_json()
    new_status = data.get('status')
    reason = data.get('reason', '')

    if new_status not in ['pending', 'paid', 'shipped', 'completed', 'cancelled']:
        return jsonify({'msg': '无效的订单状态'}), 400

    old_status = order.status
    order.status = new_status

    # 如果取消订单，恢复商品状态
    if new_status == 'cancelled' and order.item:
        order.item.status = 'on_sale'

    db.session.commit()
    log_admin_action(admin.id, '订单管理', f'修改订单状态 {old_status} -> {new_status}',
                     f'订单ID: {order_id}, 原因: {reason}', request.remote_addr)
    return jsonify(order.to_dict()), 200


@admin_bp.route('/orders/<string:order_id>/extend', methods=['PUT'])
@jwt_required()
def extend_order_time(order_id):
    """延长订单有效期（处理异常订单）"""
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    order = Order.query.get_or_404(order_id)
    data = request.get_json() or {}
    hours = data.get('hours', 24)
    reason = data.get('reason', '')

    if order.expire_time:
        order.expire_time = order.expire_time + timedelta(hours=hours)
    else:
        order.expire_time = datetime.now() + timedelta(hours=hours)

    db.session.commit()
    log_admin_action(admin.id, '订单管理', f'延长订单有效期 {hours} 小时',
                     f'订单ID: {order_id}, 原因: {reason}', request.remote_addr)
    return jsonify(order.to_dict()), 200


@admin_bp.route('/orders/<string:order_id>/refund', methods=['PUT'])
@jwt_required()
def refund_order(order_id):
    """订单退款处理"""
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    order = Order.query.get_or_404(order_id)
    data = request.get_json() or {}
    reason = data.get('reason', '')

    if order.status not in ['paid', 'shipped']:
        return jsonify({'msg': '该订单状态不支持退款'}), 400

    order.status = 'cancelled'
    if order.item:
        order.item.status = 'on_sale'

    db.session.commit()
    log_admin_action(admin.id, '订单管理', f'订单退款处理',
                     f'订单ID: {order_id}, 原因: {reason}', request.remote_addr)
    return jsonify({'msg': '退款处理成功', 'order': order.to_dict()}), 200


# ==================== 评价管理 ====================

@admin_bp.route('/reviews', methods=['GET'])
@jwt_required()
def get_reviews():
    """获取所有评价列表"""
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    search = request.args.get('search', '')
    rating = request.args.get('rating', type=int)

    query = Review.query.filter(Review.parent_id.is_(None))  # 只查主评价
    if search:
        query = query.filter(Review.content.ilike(f'%{search}%'))
    if rating:
        query = query.filter_by(rating=rating)

    total = query.count()
    reviews = query.order_by(desc(Review.created_at)).offset((page - 1) * limit).limit(limit).all()
    return jsonify({
        'reviews': [r.to_dict(include_replies=True) for r in reviews],
        'total': total
    }), 200


@admin_bp.route('/reviews/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    """删除评价"""
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    review = Review.query.get_or_404(review_id)
    data = request.get_json() or {}
    reason = data.get('reason', '')

    # 删除所有回复
    Review.query.filter_by(parent_id=review_id).delete()

    reviewer_name = review.reviewer.username if review.reviewer else 'Unknown'
    db.session.delete(review)
    db.session.commit()

    log_admin_action(admin.id, '评价管理', f'删除评价 ID:{review_id}',
                     f'评价者: {reviewer_name}, 原因: {reason}', request.remote_addr)
    return jsonify({'msg': '评价已删除'}), 200


# ==================== 公告管理 ====================

@admin_bp.route('/announcements', methods=['GET'])
@jwt_required()
def get_announcements():
    """获取公告列表"""
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    status = request.args.get('status', '')

    query = Announcement.query
    if status:
        query = query.filter_by(status=status)

    total = query.count()
    announcements = query.order_by(desc(Announcement.created_at)).offset((page - 1) * limit).limit(limit).all()
    return jsonify({'announcements': [a.to_dict() for a in announcements], 'total': total}), 200


@admin_bp.route('/announcements', methods=['POST'])
@jwt_required()
def create_announcement():
    """创建公告"""
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    data = request.get_json()

    if not data.get('title') or not data.get('content'):
        return jsonify({'msg': '标题和内容不能为空'}), 400

    announcement = Announcement(
        title=data['title'],
        content=data['content'],
        priority=data.get('priority', 'normal'),
        status=data.get('status', 'draft'),
        publisher_id=admin.id
    )

    if data.get('publish_now'):
        announcement.status = 'published'
        announcement.publish_time = datetime.now()

    if data.get('expire_time'):
        announcement.expire_time = datetime.fromisoformat(data['expire_time'].replace('Z', '+00:00'))

    db.session.add(announcement)
    db.session.commit()

    log_admin_action(admin.id, '公告管理', f'创建公告: {announcement.title}',
                     '', request.remote_addr)
    return jsonify(announcement.to_dict()), 201


@admin_bp.route('/announcements/<int:ann_id>', methods=['PUT'])
@jwt_required()
def update_announcement(ann_id):
    """更新公告"""
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    announcement = Announcement.query.get_or_404(ann_id)
    data = request.get_json()

    if 'title' in data:
        announcement.title = data['title']
    if 'content' in data:
        announcement.content = data['content']
    if 'priority' in data:
        announcement.priority = data['priority']
    if 'status' in data:
        announcement.status = data['status']
        if data['status'] == 'published' and not announcement.publish_time:
            announcement.publish_time = datetime.now()
    if 'expire_time' in data:
        if data['expire_time']:
            announcement.expire_time = datetime.fromisoformat(data['expire_time'].replace('Z', '+00:00'))
        else:
            announcement.expire_time = None

    db.session.commit()
    log_admin_action(admin.id, '公告管理', f'更新公告: {announcement.title}',
                     '', request.remote_addr)
    return jsonify(announcement.to_dict()), 200


@admin_bp.route('/announcements/<int:ann_id>', methods=['DELETE'])
@jwt_required()
def delete_announcement(ann_id):
    """删除公告"""
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    announcement = Announcement.query.get_or_404(ann_id)
    title = announcement.title
    db.session.delete(announcement)
    db.session.commit()

    log_admin_action(admin.id, '公告管理', f'删除公告: {title}',
                     '', request.remote_addr)
    return jsonify({'msg': '公告已删除'}), 200


@admin_bp.route('/announcements/<int:ann_id>/publish', methods=['PUT'])
@jwt_required()
def publish_announcement(ann_id):
    """发布公告"""
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    announcement = Announcement.query.get_or_404(ann_id)
    announcement.status = 'published'
    announcement.publish_time = datetime.now()
    db.session.commit()

    log_admin_action(admin.id, '公告管理', f'发布公告: {announcement.title}',
                     '', request.remote_addr)
    return jsonify(announcement.to_dict()), 200


# ==================== 举报管理 ====================

@admin_bp.route('/reports', methods=['GET'])
@jwt_required()
def get_reports():
    """获取举报列表"""
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    status = request.args.get('status', '')
    report_type = request.args.get('type', '')

    query = Report.query
    if status:
        query = query.filter_by(status=status)
    if report_type:
        query = query.filter_by(report_type=report_type)

    total = query.count()
    reports = query.order_by(desc(Report.created_at)).offset((page - 1) * limit).limit(limit).all()
    return jsonify({'reports': [r.to_dict() for r in reports], 'total': total}), 200


@admin_bp.route('/reports/<int:report_id>/handle', methods=['PUT'])
@jwt_required()
def handle_report(report_id):
    """处理举报"""
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    report = Report.query.get_or_404(report_id)
    data = request.get_json()

    action = data.get('action')  # resolve, reject
    result = data.get('result', '')

    if action == 'resolve':
        report.status = 'resolved'
    elif action == 'reject':
        report.status = 'rejected'
    else:
        return jsonify({'msg': '无效的操作'}), 400

    report.handler_id = admin.id
    report.handle_result = result
    report.handle_time = datetime.now()

    db.session.commit()
    log_admin_action(admin.id, '举报管理', f'处理举报 ID:{report_id}',
                     f'操作: {action}, 结果: {result}', request.remote_addr)
    return jsonify(report.to_dict()), 200


# ==================== 申诉管理 ====================

@admin_bp.route('/appeals', methods=['GET'])
@jwt_required()
def get_appeals():
    """获取申诉列表"""
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    status = request.args.get('status', '')
    appeal_type = request.args.get('type', '')

    query = Appeal.query
    if status:
        query = query.filter_by(status=status)
    if appeal_type:
        query = query.filter_by(appeal_type=appeal_type)

    total = query.count()
    appeals = query.order_by(desc(Appeal.created_at)).offset((page - 1) * limit).limit(limit).all()
    return jsonify({'appeals': [a.to_dict() for a in appeals], 'total': total}), 200


@admin_bp.route('/appeals/<int:appeal_id>/handle', methods=['PUT'])
@jwt_required()
def handle_appeal(appeal_id):
    """处理申诉"""
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    appeal = Appeal.query.get_or_404(appeal_id)
    data = request.get_json()

    action = data.get('action')  # approve, reject
    result = data.get('result', '')

    if action == 'approve':
        appeal.status = 'approved'
        # 根据申诉类型执行相应操作
        if appeal.appeal_type == 'ban':
            user = User.query.get(appeal.appellant_id)
            if user:
                user.can_publish = True
        elif appeal.appeal_type == 'item':
            item = Item.query.get(appeal.target_id)
            if item:
                item.status = 'on_sale'
    elif action == 'reject':
        appeal.status = 'rejected'
    else:
        return jsonify({'msg': '无效的操作'}), 400

    appeal.handler_id = admin.id
    appeal.handle_result = result
    appeal.handle_time = datetime.now()

    db.session.commit()
    log_admin_action(admin.id, '申诉管理', f'处理申诉 ID:{appeal_id}',
                     f'操作: {action}, 结果: {result}', request.remote_addr)
    return jsonify(appeal.to_dict()), 200


# ==================== Banner管理 ====================

@admin_bp.route('/banners', methods=['GET'])
@jwt_required()
def get_banners():
    """获取Banner列表"""
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403

    status = request.args.get('status', '')
    query = Banner.query
    if status:
        query = query.filter_by(status=status)

    banners = query.order_by(Banner.sort_order.asc(), Banner.id.desc()).all()
    return jsonify({'banners': [b.to_dict() for b in banners]}), 200


@admin_bp.route('/banners', methods=['POST'])
@jwt_required()
def create_banner():
    """创建Banner"""
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    data = request.get_json()

    if not data.get('title'):
        return jsonify({'msg': '标题不能为空'}), 400

    banner = Banner(
        title=data['title'],
        tag=data.get('tag', ''),
        description=data.get('description', ''),
        image=data.get('image', ''),
        bg_color=data.get('bg_color', 'linear-gradient(135deg, #2f3e24 0%, #1c2615 100%)'),
        emoji=data.get('emoji', '📦'),
        link=data.get('link', '/products'),
        sort_order=data.get('sort_order', 0),
        status=data.get('status', 'draft')
    )

    db.session.add(banner)
    db.session.commit()

    log_admin_action(admin.id, 'Banner管理', f'创建Banner: {banner.title}',
                     '', request.remote_addr)
    return jsonify(banner.to_dict()), 201


@admin_bp.route('/banners/<int:banner_id>', methods=['PUT'])
@jwt_required()
def update_banner(banner_id):
    """更新Banner"""
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    banner = Banner.query.get_or_404(banner_id)
    data = request.get_json()

    if 'title' in data:
        banner.title = data['title']
    if 'tag' in data:
        banner.tag = data['tag']
    if 'description' in data:
        banner.description = data['description']
    if 'image' in data:
        banner.image = data['image']
    if 'bg_color' in data:
        banner.bg_color = data['bg_color']
    if 'emoji' in data:
        banner.emoji = data['emoji']
    if 'link' in data:
        banner.link = data['link']
    if 'sort_order' in data:
        banner.sort_order = data['sort_order']
    if 'status' in data:
        banner.status = data['status']

    db.session.commit()
    log_admin_action(admin.id, 'Banner管理', f'更新Banner: {banner.title}',
                     '', request.remote_addr)
    return jsonify(banner.to_dict()), 200


@admin_bp.route('/banners/<int:banner_id>', methods=['DELETE'])
@jwt_required()
def delete_banner(banner_id):
    """删除Banner"""
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    banner = Banner.query.get_or_404(banner_id)
    title = banner.title
    db.session.delete(banner)
    db.session.commit()

    log_admin_action(admin.id, 'Banner管理', f'删除Banner: {title}',
                     '', request.remote_addr)
    return jsonify({'msg': 'Banner已删除'}), 200


@admin_bp.route('/banners/sort', methods=['PUT'])
@jwt_required()
def sort_banners():
    """批量更新Banner排序"""
    admin = require_admin()
    if not admin:
        return jsonify({'msg': 'Forbidden'}), 403
    data = request.get_json()
    orders = data.get('orders', [])  # [{id: 1, sort_order: 0}, ...]

    for item in orders:
        banner = Banner.query.get(item['id'])
        if banner:
            banner.sort_order = item['sort_order']

    db.session.commit()
    log_admin_action(admin.id, 'Banner管理', '更新Banner排序',
                     '', request.remote_addr)
    return jsonify({'msg': '排序已更新'}), 200



