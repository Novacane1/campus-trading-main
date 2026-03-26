from flask import Blueprint, request, jsonify
from app.models.models import User, UserInterest
from app import db, redis_client
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)

from sqlalchemy import or_


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({'msg': '该用户名已被占用'}), 400
    if User.query.filter_by(student_id=data.get('studentId')).first():
        return jsonify({'msg': '该学号已被注册'}), 400
    if data.get('phone') and User.query.filter_by(phone=data.get('phone')).first():
        return jsonify({'msg': '该手机号已被注册'}), 400
    if data.get('email') and User.query.filter_by(email=data.get('email')).first():
        return jsonify({'msg': '该邮箱已被注册'}), 400

    user = User(
        username=data.get('username'),
        school_name=data.get('school'),
        student_id=data.get('studentId'),
        email=data.get('email'),
        phone=data.get('phone')
    )
    user.set_password(data.get('password'))
    db.session.add(user)
    db.session.flush()  # flush to get user.id before commit

    # Save user interests
    interests = data.get('interests', [])
    for cat_id in interests:
        try:
            interest = UserInterest(user_id=user.id, category_id=cat_id)
            db.session.add(interest)
        except Exception as e:
            print(f"Error adding interest {cat_id}: {e}")

    db.session.commit()

    access_token = create_access_token(identity=str(user.id))

    try:
        if redis_client:
            redis_client.set(f"user_session:{user.id}", user.username, ex=3600)
    except Exception as e:
        print(f"Redis error: {e}")

    return jsonify({
        'msg': 'User registered successfully',
        'token': access_token,
        'user': user.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200

    data = request.get_json()
    login_id = data.get('username')
    password = data.get('password')

    if not login_id or not password:
        return jsonify({'msg': 'Username and password are required'}), 400

    user = User.query.filter(
        or_(
            User.username == login_id,
            User.email == login_id,
            User.phone == login_id,
            User.student_id == login_id
        )
    ).first()

    if not user:
        return jsonify({'msg': f'用户 "{login_id}" 不存在'}), 401

    if not user.check_password(password):
        return jsonify({'msg': '密码错误，请重试'}), 401

    access_token = create_access_token(identity=str(user.id))

    try:
        if redis_client:
            redis_client.set(f"user_session:{user.id}", user.username, ex=3600)
    except Exception as e:
        print(f"Redis error: {e}")

    return jsonify({
        'token': access_token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    try:
        if redis_client:
            redis_client.set(f"blacklist:{jti}", "true", ex=3600)
    except Exception:
        pass
    return jsonify({'msg': 'Logged out successfully'}), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify(user.to_dict()), 200


@auth_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()
    old_password = data.get('oldPassword') or data.get('old_password')
    new_password = data.get('newPassword') or data.get('new_password')
    if not old_password or not new_password:
        return jsonify({'msg': '请填写旧密码和新密码'}), 400
    if not user.check_password(old_password):
        return jsonify({'msg': '旧密码错误'}), 400
    user.set_password(new_password)
    db.session.commit()
    return jsonify({'msg': '密码修改成功'}), 200


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()
    if 'username' in data:
        existing = User.query.filter(User.username == data['username'], User.id != user.id).first()
        if existing:
            return jsonify({'msg': '用户名已被占用'}), 400
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    if 'phone' in data:
        user.phone = data['phone']
    if 'school_name' in data or 'school' in data:
        user.school_name = data.get('school_name') or data.get('school')
    db.session.commit()
    return jsonify(user.to_dict()), 200
