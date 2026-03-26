from flask import Blueprint, request, jsonify
from app.models.models import Application
from app import db
from flask_jwt_extended import jwt_required, get_jwt_identity

applications_bp = Blueprint('applications', __name__)


@applications_bp.route('/', methods=['POST'])
@jwt_required()
def submit_application():
    user_id = get_jwt_identity()
    data = request.get_json()
    app_type = data.get('type')
    name = data.get('name')
    if app_type not in ('category', 'location'):
        return jsonify({'msg': '申请类型无效，可选: category, location'}), 400
    if not name:
        return jsonify({'msg': '名称不能为空'}), 400
    existing = Application.query.filter_by(
        user_id=user_id, app_type=app_type, name=name, status='pending'
    ).first()
    if existing:
        return jsonify({'msg': '您已提交过相同的申请，请等待审核'}), 400
    app = Application(
        user_id=user_id,
        app_type=app_type,
        name=name,
        description=data.get('description', '')
    )
    db.session.add(app)
    db.session.commit()
    return jsonify(app.to_dict()), 201


@applications_bp.route('/me', methods=['GET'])
@jwt_required()
def my_applications():
    user_id = get_jwt_identity()
    apps = Application.query.filter_by(user_id=user_id).order_by(
        Application.created_at.desc()
    ).all()
    return jsonify({'applications': [a.to_dict() for a in apps]}), 200
