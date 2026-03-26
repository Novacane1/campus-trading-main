from flask import Blueprint, jsonify, request
from app.models.models import Announcement
from sqlalchemy import desc
from datetime import datetime

announcement_bp = Blueprint('announcements', __name__)


@announcement_bp.route('/', methods=['GET'])
def get_public_announcements():
    """获取已发布的公告列表（公开接口）"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)

    now = datetime.now()
    query = Announcement.query.filter(
        Announcement.status == 'published',
        # 未过期或没有设置过期时间
        (Announcement.expire_time.is_(None)) | (Announcement.expire_time > now)
    )

    total = query.count()
    announcements = query.order_by(
        # 紧急公告优先
        desc(Announcement.priority == 'urgent'),
        desc(Announcement.priority == 'high'),
        desc(Announcement.publish_time)
    ).offset((page - 1) * limit).limit(limit).all()

    return jsonify({
        'announcements': [a.to_dict() for a in announcements],
        'total': total
    }), 200


@announcement_bp.route('/latest', methods=['GET'])
def get_latest_announcements():
    """获取最新公告（用于首页展示）"""
    limit = request.args.get('limit', 5, type=int)

    now = datetime.now()
    announcements = Announcement.query.filter(
        Announcement.status == 'published',
        (Announcement.expire_time.is_(None)) | (Announcement.expire_time > now)
    ).order_by(
        desc(Announcement.priority == 'urgent'),
        desc(Announcement.priority == 'high'),
        desc(Announcement.publish_time)
    ).limit(limit).all()

    return jsonify({
        'announcements': [a.to_dict() for a in announcements]
    }), 200


@announcement_bp.route('/<int:ann_id>', methods=['GET'])
def get_announcement_detail(ann_id):
    """获取公告详情"""
    announcement = Announcement.query.get_or_404(ann_id)

    # 只返回已发布的公告
    if announcement.status != 'published':
        return jsonify({'msg': '公告不存在'}), 404

    return jsonify(announcement.to_dict()), 200
