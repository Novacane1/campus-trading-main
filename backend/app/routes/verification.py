from flask import Blueprint, request, jsonify
from app.models.models import StudentVerification, User

verification_bp = Blueprint('verification', __name__)


@verification_bp.route('/verify-student', methods=['POST'])
def verify_student():
    """验证学生身份（模拟学信网接口）"""
    data = request.get_json()
    school = data.get('school')
    student_id = data.get('studentId')
    real_name = data.get('realName')

    if not school or not student_id or not real_name:
        return jsonify({'verified': False, 'msg': '请填写完整的学校、学号和真实姓名'}), 400

    # 检查该学号是否已被注册
    existing_user = User.query.filter_by(student_id=student_id).first()
    if existing_user:
        return jsonify({'verified': False, 'msg': '该学号已被注册，请勿重复注册'}), 200

    record = StudentVerification.query.filter_by(
        school_name=school,
        student_id=student_id,
        real_name=real_name
    ).first()

    if record:
        return jsonify({'verified': True, 'msg': '学生身份验证通过'}), 200
    else:
        return jsonify({'verified': False, 'msg': '验证失败，学校、学号或姓名不匹配'}), 200


@verification_bp.route('/schools', methods=['GET'])
def get_schools():
    """获取所有可选学校列表"""
    schools = StudentVerification.query.with_entities(
        StudentVerification.school_name
    ).distinct().order_by(StudentVerification.school_name).all()
    return jsonify([s[0] for s in schools]), 200
