from flask import Blueprint, request, jsonify
from app.models.models import Message, User
from app import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_, func, desc
from app.services.risk_control import RiskControlService

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    user_id = int(get_jwt_identity())
    # Get latest message per conversation partner
    subq = db.session.query(
        func.greatest(Message.sender_id, Message.receiver_id).label('u1'),
        func.least(Message.sender_id, Message.receiver_id).label('u2'),
        func.max(Message.id).label('max_id')
    ).filter(
        or_(Message.sender_id == user_id, Message.receiver_id == user_id)
    ).group_by('u1', 'u2').subquery()

    messages = Message.query.join(
        subq, Message.id == subq.c.max_id
    ).order_by(desc(Message.created_at)).all()

    conversations = []
    for msg in messages:
        partner_id = msg.receiver_id if msg.sender_id == user_id else msg.sender_id
        partner = User.query.get(partner_id)
        unread = Message.query.filter_by(
            sender_id=partner_id, receiver_id=user_id, is_read=False
        ).count()
        conversations.append({
            'id': partner_id,
            'other_user': partner.to_dict() if partner else None,
            'last_message': {
                'id': msg.id,
                'content': msg.content,
                'sender_id': msg.sender_id,
                'created_at': msg.created_at.isoformat() if msg.created_at else None
            },
            'unread_count': unread
        })
    return jsonify({'chats': conversations}), 200


@chat_bp.route('/messages/<int:partner_id>', methods=['GET'])
@jwt_required()
def get_messages(partner_id):
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    messages = Message.query.filter(
        or_(
            and_(Message.sender_id == user_id, Message.receiver_id == partner_id),
            and_(Message.sender_id == partner_id, Message.receiver_id == user_id)
        )
    ).order_by(desc(Message.created_at)).offset((page - 1) * limit).limit(limit).all()
    messages.reverse()
    return jsonify({'messages': [m.to_dict() for m in messages]}), 200


@chat_bp.route('/messages/<int:partner_id>', methods=['POST'])
@jwt_required()
def send_message(partner_id):
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    content = (data.get('content') or '').strip()
    msg_type = data.get('type', 'text')
    if not content:
        return jsonify({'msg': '消息内容不能为空'}), 400
    safety_check = RiskControlService.check_content_safety(content)
    if not safety_check['safe']:
        return jsonify({'msg': safety_check['reason']}), 400
    partner = db.session.get(User, partner_id)
    if not partner:
        return jsonify({'msg': '用户不存在'}), 404
    message = Message(
        sender_id=user_id,
        receiver_id=partner_id,
        content=content,
        msg_type=msg_type
    )
    db.session.add(message)
    db.session.commit()
    RiskControlService.log_action(
        user_id=user_id,
        action_type='message',
        target_id=partner_id,
        ip_address=request.remote_addr,
        device_id=request.headers.get('X-Device-ID'),
        content=content
    )
    return jsonify(message.to_dict()), 201


@chat_bp.route('/messages/<int:partner_id>/read', methods=['PUT'])
@jwt_required()
def mark_as_read(partner_id):
    user_id = int(get_jwt_identity())
    Message.query.filter_by(
        sender_id=partner_id, receiver_id=user_id, is_read=False
    ).update({'is_read': True})
    db.session.commit()
    return jsonify({'msg': 'Messages marked as read'}), 200


@chat_bp.route('/messages/<int:message_id>/mark-read', methods=['PUT'])
@jwt_required()
def mark_message_read(message_id):
    user_id = int(get_jwt_identity())
    msg = Message.query.get_or_404(message_id)
    if msg.receiver_id == user_id:
        msg.is_read = True
        db.session.commit()
    return jsonify({'msg': 'ok'}), 200


@chat_bp.route('/messages/read-all', methods=['PUT'])
@jwt_required()
def mark_all_read():
    user_id = int(get_jwt_identity())
    Message.query.filter_by(receiver_id=user_id, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'msg': 'All messages marked as read'}), 200


@chat_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    user_id = int(get_jwt_identity())
    count = Message.query.filter_by(receiver_id=user_id, is_read=False).count()
    return jsonify({'count': count}), 200


@chat_bp.route('/conversations/<int:partner_id>', methods=['DELETE'])
@jwt_required()
def delete_conversation(partner_id):
    user_id = int(get_jwt_identity())
    Message.query.filter(
        or_(
            and_(Message.sender_id == user_id, Message.receiver_id == partner_id),
            and_(Message.sender_id == partner_id, Message.receiver_id == user_id)
        )
    ).delete(synchronize_session=False)
    db.session.commit()
    return jsonify({'msg': 'Conversation deleted'}), 200
