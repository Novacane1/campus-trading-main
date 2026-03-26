"""
评价系统API路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.models import Review, Order, User, Item
from app.services.risk_control import RiskControlService

review_bp = Blueprint('review', __name__, url_prefix='/api/reviews')


@review_bp.route('/item/<int:item_id>', methods=['GET'])
def get_item_reviews(item_id):
    """获取商品的所有顶级评价（含嵌套回复）"""
    try:
        reviews = Review.query.filter_by(
            item_id=item_id,
            parent_id=None
        ).order_by(Review.created_at.desc()).all()
        return jsonify([r.to_dict(include_replies=True) for r in reviews]), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@review_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_reviews(user_id):
    """获取用户收到的所有评价"""
    try:
        reviews = Review.query.filter_by(
            reviewed_user_id=user_id,
            parent_id=None
        ).order_by(Review.created_at.desc()).all()

        # 计算平均评分（只统计有评分的顶级评价）
        rated_reviews = [r for r in reviews if r.rating is not None]
        if rated_reviews:
            avg_rating = sum(r.rating for r in rated_reviews) / len(rated_reviews)
        else:
            avg_rating = 0

        return jsonify({
            'reviews': [r.to_dict(include_replies=True) for r in reviews],
            'avg_rating': round(avg_rating, 1),
            'total_count': len(reviews)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@review_bp.route('/seller/<int:seller_id>', methods=['GET'])
def get_seller_reviews(seller_id):
    """获取卖家收到的评价（买家对卖家的评价）"""
    try:
        reviews = Review.query.filter_by(
            reviewed_user_id=seller_id,
            review_type='buyer_to_seller',
            parent_id=None
        ).order_by(Review.created_at.desc()).all()

        rated_reviews = [r for r in reviews if r.rating is not None]
        if rated_reviews:
            avg_rating = sum(r.rating for r in rated_reviews) / len(rated_reviews)
        else:
            avg_rating = 0

        return jsonify({
            'reviews': [r.to_dict(include_replies=True) for r in reviews],
            'avg_rating': round(avg_rating, 1),
            'total_count': len(reviews)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@review_bp.route('/', methods=['POST'])
@jwt_required()
def create_review():
    """创建评价（支持订单评价和直接商品评价）"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        order_id = data.get('order_id')
        item_id = data.get('item_id')
        rating = data.get('rating')
        content = data.get('content', '')
        is_anonymous = data.get('is_anonymous', False)

        if not rating:
            return jsonify({'error': '评分是必填项'}), 400

        if rating < 1 or rating > 5:
            return jsonify({'error': '评分必须在1-5之间'}), 400

        # 内容安全检查
        if content:
            safety_check = RiskControlService.check_content_safety(content)
            if not safety_check['safe']:
                return jsonify({'error': safety_check['reason']}), 400

        review_type = 'direct'
        reviewed_user_id = None
        target_item_id = item_id

        if order_id:
            # 基于订单的评价
            order = Order.query.get(order_id)
            if not order:
                return jsonify({'error': '订单不存在'}), 404

            if order.status != 'completed':
                return jsonify({'error': '只能对已完成的订单进行评价'}), 400

            if current_user_id == order.buyer_id:
                review_type = 'buyer_to_seller'
                reviewed_user_id = order.item.seller_id
            elif current_user_id == order.item.seller_id:
                review_type = 'seller_to_buyer'
                reviewed_user_id = order.buyer_id
            else:
                return jsonify({'error': '您无权评价此订单'}), 403

            # 检查是否已评价该订单
            existing = Review.query.filter_by(
                order_id=order_id,
                reviewer_id=current_user_id,
                parent_id=None
            ).first()
            if existing:
                return jsonify({'error': '您已经评价过此订单'}), 400

            target_item_id = order.item_id
        else:
            # 直接商品评价（无订单）
            if not item_id:
                return jsonify({'error': '商品ID是必填项'}), 400

            item = Item.query.get(item_id)
            if not item:
                return jsonify({'error': '商品不存在'}), 404

            reviewed_user_id = item.seller_id
            target_item_id = item_id

        # 创建评价
        review = Review(
            order_id=order_id,
            reviewer_id=current_user_id,
            reviewed_user_id=reviewed_user_id,
            item_id=target_item_id,
            rating=rating,
            content=content,
            review_type=review_type,
            is_anonymous=is_anonymous
        )
        db.session.add(review)

        # 更新被评价用户的信用分
        if reviewed_user_id:
            reviewed_user = User.query.get(reviewed_user_id)
            if reviewed_user:
                if rating >= 4:
                    reviewed_user.credit_score = min(100, reviewed_user.credit_score + 2)
                elif rating <= 2:
                    reviewed_user.credit_score = max(0, reviewed_user.credit_score - 3)

        # 记录风控日志
        RiskControlService.log_action(
            user_id=current_user_id,
            action_type='review',
            target_id=target_item_id,
            content=content
        )

        db.session.commit()

        return jsonify({
            'message': '评价成功',
            'review': review.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@review_bp.route('/reply', methods=['POST'])
@jwt_required()
def reply_to_review():
    """回复评价"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        parent_id = data.get('parent_id')
        content = data.get('content', '').strip()

        if not parent_id:
            return jsonify({'error': '缺少父评价ID'}), 400

        if not content:
            return jsonify({'error': '回复内容不能为空'}), 400

        # 获取父评价
        parent_review = Review.query.get(parent_id)
        if not parent_review:
            return jsonify({'error': '评价不存在'}), 404

        # 内容安全检查
        safety_check = RiskControlService.check_content_safety(content)
        if not safety_check['safe']:
            return jsonify({'error': safety_check['reason']}), 400

        # 创建回复
        reply = Review(
            reviewer_id=current_user_id,
            item_id=parent_review.item_id,
            content=content,
            review_type='reply',
            parent_id=parent_id
        )
        db.session.add(reply)
        db.session.commit()

        return jsonify({
            'message': '回复成功',
            'reply': reply.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@review_bp.route('/item/<int:item_id>/reviewable-orders', methods=['GET'])
@jwt_required(optional=True)
def get_reviewable_orders(item_id):
    """获取当前用户对某商品可评价的订单列表"""
    current_user_id = get_jwt_identity()
    if not current_user_id:
        return jsonify([]), 200
    try:
        from sqlalchemy import and_

        # 查找该用户与该商品相关的已完成订单
        orders = Order.query.filter(
            and_(
                Order.item_id == item_id,
                Order.status == 'completed',
                (Order.buyer_id == current_user_id) | (Order.item.has(seller_id=current_user_id))
            )
        ).all()

        reviewable = []
        for order in orders:
            # 检查是否已评价
            existing = Review.query.filter_by(
                order_id=order.id,
                reviewer_id=current_user_id,
                parent_id=None
            ).first()
            if not existing:
                reviewable.append({
                    'order_id': str(order.id),
                    'item_title': order.item.name if order.item else '',
                    'created_at': order.created_at.isoformat() if order.created_at else None
                })

        return jsonify(reviewable), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@review_bp.route('/order/<order_id>/status', methods=['GET'])
@jwt_required()
def get_review_status(order_id):
    """检查订单的评价状态"""
    try:
        current_user_id = get_jwt_identity()
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': '订单不存在'}), 404

        # 检查当前用户是否已评价（只看顶级评价）
        my_review = Review.query.filter_by(
            order_id=order_id,
            reviewer_id=current_user_id,
            parent_id=None
        ).first()

        # 检查对方是否已评价
        if current_user_id == order.buyer_id:
            other_user_id = order.item.seller_id
        else:
            other_user_id = order.buyer_id

        other_review = Review.query.filter_by(
            order_id=order_id,
            reviewer_id=other_user_id,
            parent_id=None
        ).first()

        return jsonify({
            'can_review': order.status == 'completed' and my_review is None,
            'my_review': my_review.to_dict() if my_review else None,
            'other_reviewed': other_review is not None
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
