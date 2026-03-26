from flask import Blueprint, jsonify
from app.models.models import Banner
from sqlalchemy import asc

banner_bp = Blueprint('banners', __name__)


@banner_bp.route('/', methods=['GET'])
def get_banners():
    """获取已发布的Banner列表（公开接口）"""
    banners = Banner.query.filter_by(status='published').order_by(asc(Banner.sort_order)).all()
    return jsonify({
        'banners': [b.to_dict() for b in banners]
    }), 200
