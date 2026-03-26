"""
风控服务模块
实现轻量级风控规则，追踪异常行为并自动打标
"""
from datetime import datetime, timedelta
from app import db
from app.models.models import RiskLog, UserRiskTag, User
import re


# 敏感关键词列表
SENSITIVE_KEYWORDS = [
    '微信', 'QQ', '支付宝', '转账', '私下交易', '线下付款',
    '假货', '盗版', '走私', '违禁', '毒品', '枪支',
    '赌博', '色情', '诈骗', '传销', '非法'
]

# 风控阈值配置
RISK_THRESHOLDS = {
    'review_count_1h': 10,  # 1小时内评价次数
    'price_change_1h': 5,   # 1小时内改价次数
    'price_change_24h': 15, # 24小时内改价次数
    'same_ip_users': 3,     # 同IP用户数
    'same_device_users': 3  # 同设备用户数
}


class RiskControlService:
    """风控服务类"""

    @staticmethod
    def log_action(user_id, action_type, target_id=None, ip_address=None,
                   device_id=None, content=None):
        """记录用户行为日志"""
        risk_score = 0

        # 检测敏感关键词
        if content and action_type in ['review', 'message', 'item_desc']:
            if RiskControlService._contains_sensitive_keywords(content):
                risk_score += 50

        log = RiskLog(
            user_id=user_id,
            action_type=action_type,
            target_id=target_id,
            ip_address=ip_address,
            device_id=device_id,
            content=content,
            risk_score=risk_score
        )
        db.session.add(log)
        db.session.commit()

        # 异步检查风险
        RiskControlService._check_risk_patterns(user_id, action_type, ip_address, device_id)

        return log

    @staticmethod
    def _contains_sensitive_keywords(text):
        """检测文本是否包含敏感关键词"""
        if not text:
            return False
        text_lower = text.lower()
        for keyword in SENSITIVE_KEYWORDS:
            if keyword in text_lower or keyword.lower() in text_lower:
                return True
        return False

    @staticmethod
    def _check_risk_patterns(user_id, action_type, ip_address=None, device_id=None):
        """检查风险模式并自动打标"""
        now = datetime.now()

        # 检查频繁评价
        if action_type == 'review':
            one_hour_ago = now - timedelta(hours=1)
            review_count = RiskLog.query.filter(
                RiskLog.user_id == user_id,
                RiskLog.action_type == 'review',
                RiskLog.created_at >= one_hour_ago
            ).count()

            if review_count >= RISK_THRESHOLDS['review_count_1h']:
                RiskControlService._add_risk_tag(
                    user_id,
                    'frequent_review',
                    'high',
                    f'1小时内评价{review_count}次，疑似刷单'
                )

        # 检查频繁改价
        if action_type == 'price_change':
            one_hour_ago = now - timedelta(hours=1)
            one_day_ago = now - timedelta(days=1)

            price_change_1h = RiskLog.query.filter(
                RiskLog.user_id == user_id,
                RiskLog.action_type == 'price_change',
                RiskLog.created_at >= one_hour_ago
            ).count()

            price_change_24h = RiskLog.query.filter(
                RiskLog.user_id == user_id,
                RiskLog.action_type == 'price_change',
                RiskLog.created_at >= one_day_ago
            ).count()

            if price_change_1h >= RISK_THRESHOLDS['price_change_1h']:
                RiskControlService._add_risk_tag(
                    user_id,
                    'price_abuse',
                    'high',
                    f'1小时内改价{price_change_1h}次，疑似价格操纵'
                )
            elif price_change_24h >= RISK_THRESHOLDS['price_change_24h']:
                RiskControlService._add_risk_tag(
                    user_id,
                    'price_abuse',
                    'medium',
                    f'24小时内改价{price_change_24h}次'
                )

        # 检查同IP异常
        if ip_address:
            RiskControlService._check_same_ip(user_id, ip_address)

        # 检查同设备异常
        if device_id:
            RiskControlService._check_same_device(user_id, device_id)

    @staticmethod
    def _check_same_ip(user_id, ip_address):
        """检查同IP多账号"""
        one_day_ago = datetime.now() - timedelta(days=1)

        # 查询24小时内使用相同IP的不同用户
        same_ip_users = db.session.query(RiskLog.user_id).filter(
            RiskLog.ip_address == ip_address,
            RiskLog.created_at >= one_day_ago
        ).distinct().all()

        if len(same_ip_users) >= RISK_THRESHOLDS['same_ip_users']:
            for (uid,) in same_ip_users:
                RiskControlService._add_risk_tag(
                    uid,
                    'same_ip_multi_account',
                    'medium',
                    f'IP {ip_address} 关联{len(same_ip_users)}个账号'
                )

    @staticmethod
    def _check_same_device(user_id, device_id):
        """检查同设备多账号"""
        one_day_ago = datetime.now() - timedelta(days=1)

        # 查询24小时内使用相同设备的不同用户
        same_device_users = db.session.query(RiskLog.user_id).filter(
            RiskLog.device_id == device_id,
            RiskLog.created_at >= one_day_ago
        ).distinct().all()

        if len(same_device_users) >= RISK_THRESHOLDS['same_device_users']:
            for (uid,) in same_device_users:
                RiskControlService._add_risk_tag(
                    uid,
                    'same_device_multi_account',
                    'medium',
                    f'设备 {device_id[:8]}... 关联{len(same_device_users)}个账号'
                )

    @staticmethod
    def _add_risk_tag(user_id, tag_type, severity, detail):
        """添加风险标签（避免重复）"""
        # 检查是否已存在相同标签
        existing_tag = UserRiskTag.query.filter_by(
            user_id=user_id,
            tag_type=tag_type
        ).first()

        if existing_tag:
            # 更新现有标签
            existing_tag.severity = severity
            existing_tag.detail = detail
            existing_tag.created_at = datetime.now()
            existing_tag.expires_at = datetime.now() + timedelta(days=7)
        else:
            # 创建新标签
            tag = UserRiskTag(
                user_id=user_id,
                tag_type=tag_type,
                severity=severity,
                detail=detail,
                auto_tagged=True,
                expires_at=datetime.now() + timedelta(days=7)
            )
            db.session.add(tag)

        db.session.commit()

    @staticmethod
    def get_user_risk_tags(user_id):
        """获取用户的风险标签"""
        tags = UserRiskTag.query.filter_by(user_id=user_id).filter(
            (UserRiskTag.expires_at == None) | (UserRiskTag.expires_at > datetime.now())
        ).all()
        return [tag.to_dict() for tag in tags]

    @staticmethod
    def get_safety_tips(user_id=None):
        """生成安全提示（可选传入user_id获取个性化提示）"""
        tips = []

        # 基础安全提示（所有用户都能看到）
        tips.append({
            'type': 'info',
            'title': '交易安全提示',
            'content': '建议在公共区域面交，保留平台内沟通记录'
        })
        tips.append({
            'type': 'info',
            'title': '支付安全',
            'content': '请使用平台内交易，切勿私下转账或扫码付款'
        })
        tips.append({
            'type': 'info',
            'title': '验货提醒',
            'content': '当面验货确认无误后再完成交易，避免纠纷'
        })

        # 如果有user_id，添加个性化提示
        if user_id:
            tags = RiskControlService.get_user_risk_tags(user_id)
            for tag in tags:
                if tag['tag_type'] == 'frequent_review':
                    tips.append({
                        'type': 'warning',
                        'title': '异常评价行为',
                        'content': '检测到您的评价行为异常，请确保真实交易后再评价'
                    })
                elif tag['tag_type'] == 'price_abuse':
                    tips.append({
                        'type': 'warning',
                        'title': '频繁改价提醒',
                        'content': '频繁修改价格可能影响商品曝光，建议合理定价'
                    })
                elif tag['tag_type'] == 'keyword_violation':
                    tips.append({
                        'type': 'danger',
                        'title': '内容违规警告',
                        'content': '您的内容包含敏感词汇，请遵守平台规则'
                    })
                elif 'multi_account' in tag['tag_type']:
                    tips.append({
                        'type': 'warning',
                        'title': '账号安全提醒',
                        'content': '检测到异常登录行为，请注意账号安全'
                    })

        return tips

    @staticmethod
    def check_content_safety(content):
        """检查内容安全性"""
        if RiskControlService._contains_sensitive_keywords(content):
            return {
                'safe': False,
                'reason': '内容包含敏感关键词，请修改后重试',
                'keywords': [kw for kw in SENSITIVE_KEYWORDS if kw in content or kw.lower() in content.lower()]
            }
        return {'safe': True}
