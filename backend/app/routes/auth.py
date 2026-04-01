from flask import Blueprint, request, jsonify
from app.models.models import User, UserInterest
from app import db, redis_client
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from datetime import timedelta
import secrets

auth_bp = Blueprint('auth', __name__)

from sqlalchemy import or_


def _normalize_string_list(values, max_len=64):
    if not isinstance(values, list):
        return []
    normalized = []
    seen = set()
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if not text:
            continue
        text = text[:max_len]
        if text not in seen:
            seen.add(text)
            normalized.append(text)
    return normalized


def _store_temp_token(prefix, user_id, ttl=1800):
    if not redis_client:
        return None
    token = secrets.token_urlsafe(24)
    redis_client.setex(f'{prefix}:{token}', ttl, str(user_id))
    return token


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


@auth_bp.route('/verify-phone', methods=['POST'])
@jwt_required()
def verify_phone():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': '用户不存在'}), 404
    if not user.phone:
        return jsonify({'msg': '请先绑定手机号'}), 400
    user.phone_verified = True
    db.session.commit()
    return jsonify({'msg': '手机号验证成功', 'user': user.to_dict()}), 200


@auth_bp.route('/verify-email', methods=['POST'])
@jwt_required()
def verify_email_direct():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': '用户不存在'}), 404
    if not user.email:
        return jsonify({'msg': '请先绑定邮箱'}), 400
    user.email_verified = True
    db.session.commit()
    return jsonify({'msg': '邮箱验证成功', 'user': user.to_dict()}), 200


@auth_bp.route('/verify-email/<token>', methods=['GET'])
def verify_email_with_token(token):
    if not redis_client:
        return jsonify({'msg': '当前环境不支持邮箱验证'}), 400
    user_id = redis_client.get(f'email_verify:{token}')
    if not user_id:
        return jsonify({'msg': '验证链接无效或已过期'}), 400
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': '用户不存在'}), 404
    user.email_verified = True
    db.session.commit()
    redis_client.delete(f'email_verify:{token}')
    return jsonify({'msg': '邮箱验证成功', 'user': user.to_dict()}), 200


@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification_email():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip()
    if not email:
        return jsonify({'msg': '请输入邮箱'}), 400
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'msg': '如果邮箱存在，验证邮件已发送'}), 200
    token = _store_temp_token('email_verify', user.id, ttl=3600)
    return jsonify({
        'msg': '验证邮件已发送',
        'verify_token': token
    }), 200


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip()
    if not email:
        return jsonify({'msg': '请输入邮箱'}), 400
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'msg': '如果邮箱存在，重置链接已发送'}), 200
    token = _store_temp_token('password_reset', user.id, ttl=1800)
    return jsonify({
        'msg': '重置链接已发送',
        'reset_token': token
    }), 200


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json() or {}
    token = (data.get('token') or '').strip()
    new_password = (data.get('newPassword') or data.get('new_password') or '').strip()
    if not token or not new_password:
        return jsonify({'msg': '缺少重置令牌或新密码'}), 400
    if len(new_password) < 6:
        return jsonify({'msg': '新密码长度至少6位'}), 400
    if not redis_client:
        return jsonify({'msg': '当前环境不支持密码重置'}), 400
    user_id = redis_client.get(f'password_reset:{token}')
    if not user_id:
        return jsonify({'msg': '重置令牌无效或已过期'}), 400
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': '用户不存在'}), 404
    user.set_password(new_password)
    db.session.commit()
    redis_client.delete(f'password_reset:{token}')
    return jsonify({'msg': '密码重置成功'}), 200


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json() or {}
    if 'username' in data:
        existing = User.query.filter(User.username == data['username'], User.id != user.id).first()
        if existing:
            return jsonify({'msg': '用户名已被占用'}), 400
        user.username = data['username']
    if 'student_id' in data or 'studentId' in data:
        student_id = (data.get('student_id') or data.get('studentId') or '').strip()
        if not student_id:
            return jsonify({'msg': '学号不能为空'}), 400
        existing = User.query.filter(User.student_id == student_id, User.id != user.id).first()
        if existing:
            return jsonify({'msg': '该学号已被占用'}), 400
        user.student_id = student_id
    if 'email' in data:
        email = (data.get('email') or '').strip() or None
        if email:
            existing = User.query.filter(User.email == email, User.id != user.id).first()
            if existing:
                return jsonify({'msg': '该邮箱已被占用'}), 400
        if user.email != email:
            user.email_verified = False
        user.email = email
    if 'phone' in data:
        phone = (data.get('phone') or '').strip() or None
        if phone:
            existing = User.query.filter(User.phone == phone, User.id != user.id).first()
            if existing:
                return jsonify({'msg': '该手机号已被占用'}), 400
        if user.phone != phone:
            user.phone_verified = False
        user.phone = phone
    if 'school_name' in data or 'school' in data:
        user.school_name = data.get('school_name') or data.get('school')
    if 'usual_time_slots' in data:
        user.usual_time_slots = _normalize_string_list(data.get('usual_time_slots'), max_len=64) or None
    if 'usual_locations' in data:
        user.usual_locations = _normalize_string_list(data.get('usual_locations'), max_len=64) or None
    db.session.commit()
    return jsonify(user.to_dict()), 200
