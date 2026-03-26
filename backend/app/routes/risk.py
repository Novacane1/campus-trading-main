"""
风控相关API路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.risk_control import RiskControlService
from app.models.models import UserRiskTag

risk_bp = Blueprint('risk', __name__, url_prefix='/api/risk')


@risk_bp.route('/safety-tips', methods=['GET'])
def get_safety_tips():
    """获取安全提示（无需登录）"""
    try:
        tips = RiskControlService.get_safety_tips()
        return jsonify(tips), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@risk_bp.route('/check-content', methods=['POST'])
@jwt_required()
def check_content():
    """检查内容安全性"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        content = data.get('content', '')

        result = RiskControlService.check_content_safety(content)

        # 如果不安全，记录日志
        if not result['safe']:
            RiskControlService.log_action(
                user_id=current_user_id,
                action_type='keyword_violation',
                content=content,
                ip_address=request.remote_addr,
                device_id=request.headers.get('X-Device-ID')
            )

            # 添加风险标签
            RiskControlService._add_risk_tag(
                current_user_id,
                'keyword_violation',
                'high',
                f'内容包含敏感词: {", ".join(result.get("keywords", []))}'
            )

        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@risk_bp.route('/log-action', methods=['POST'])
@jwt_required()
def log_action():
    """记录用户行为（供前端调用）"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        action_type = data.get('action_type')
        target_id = data.get('target_id')
        content = data.get('content')

        log = RiskControlService.log_action(
            user_id=current_user_id,
            action_type=action_type,
            target_id=target_id,
            ip_address=request.remote_addr,
            device_id=request.headers.get('X-Device-ID'),
            content=content
        )

        return jsonify({'success': True, 'log_id': log.id}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@risk_bp.route('/user-tags', methods=['GET'])
@jwt_required()
def get_user_tags():
    """获取用户风险标签"""
    try:
        current_user_id = get_jwt_identity()
        tags = RiskControlService.get_user_risk_tags(current_user_id)
        return jsonify(tags), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
