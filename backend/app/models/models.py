import uuid
from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import UUID, ARRAY


# ==================== 5 核心表（按用户规范） ====================

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    school_name = db.Column(db.String(128))
    student_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(11))
    credit_score = db.Column(db.Integer, default=60)
    email = db.Column(db.String(120))
    password_hash = db.Column(db.String(256))
    can_publish = db.Column(db.Boolean, default=True)

    # 用户常用时间和地点
    usual_time_slots = db.Column(ARRAY(db.String))  # 常用时间段
    usual_locations = db.Column(ARRAY(db.String))  # 常用地点

    items = db.relationship('Item', backref='seller', lazy='dynamic')
    orders = db.relationship('Order', backref='buyer', lazy='dynamic')
    actions = db.relationship('UserAction', backref='user', lazy='dynamic')
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy='dynamic')
    cart_items = db.relationship('CartItem', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'school_name': self.school_name,
            'student_id': self.student_id,
            'phone': self.phone,
            'credit_score': self.credit_score,
            'email': self.email,
            'can_publish': self.can_publish,
            'usual_time_slots': self.usual_time_slots or [],
            'usual_locations': self.usual_locations or [],
        }


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(64), nullable=False, unique=True)
    parent_id = db.Column(UUID(as_uuid=True), db.ForeignKey('categories.id'))
    icon = db.Column(db.String(64))
    sort_order = db.Column(db.Integer, default=0)

    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]))
    items = db.relationship('Item', backref='category', lazy='dynamic')

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'parent_id': str(self.parent_id) if self.parent_id else None,
            'icon': self.icon,
            'sort_order': self.sort_order,
            'productCount': self.items.filter_by(status='on_sale').count()
        }


class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False, index=True)
    category_id = db.Column(UUID(as_uuid=True), db.ForeignKey('categories.id'), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    images = db.Column(ARRAY(db.String))
    condition = db.Column(db.String(20))  # 全新、几乎全新、稍有瑕疵、瑕疵较多、7成新以下
    location = db.Column(db.String(128))
    status = db.Column(db.String(20), default='on_sale')  # on_sale, sold, locked, deleted
    quantity = db.Column(db.Integer, default=1)  # 库存数量
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 时空约束字段
    available_time_slots = db.Column(ARRAY(db.String))  # 可交易时间窗 ["周一 08:00-12:00", "周三 14:00-18:00"]
    preferred_locations = db.Column(ARRAY(db.String))  # 常用活动地点 ["图书馆", "食堂"]

    orders = db.relationship('Order', backref='item', lazy='dynamic')
    actions = db.relationship('UserAction', backref='item', lazy='dynamic')
    cart_entries = db.relationship('CartItem', backref='item', lazy='dynamic')

    def to_dict(self, include_seller=False):
        # 计算浏览数和收藏数
        views_count = self.actions.filter_by(action_type='view').count()
        favorites_count = self.actions.filter_by(action_type='fav').count()
        data = {
            'id': self.id,
            'seller_id': self.seller_id,
            'category_id': str(self.category_id) if self.category_id else None,
            'name': self.name,
            'description': self.description,
            'price': float(self.price),
            'images': self.images or [],
            'condition': self.condition,
            'location': self.location,
            'status': self.status,
            'quantity': self.quantity or 1,
            'views': views_count,
            'favorites': favorites_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'available_time_slots': self.available_time_slots or [],
            'preferred_locations': self.preferred_locations or [],
        }
        if include_seller and self.seller:
            data['seller'] = self.seller.to_dict()
        return data


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, default=1)  # 购买数量
    status = db.Column(db.String(20), default='pending')  # pending, paid, shipped, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.now)
    expire_time = db.Column(db.DateTime, nullable=True)  # 15分钟后超时自动取消

    def to_dict(self):
        data = {
            'id': str(self.id),
            'buyer_id': self.buyer_id,
            'item_id': self.item_id,
            'amount': float(self.amount),
            'quantity': self.quantity or 1,
            'total_price': float(self.amount),
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expire_time': self.expire_time.isoformat() if self.expire_time else None,
        }
        if self.item:
            data['item'] = self.item.to_dict(include_seller=True)
            data['item_title'] = self.item.name
            data['item_image'] = (self.item.images or [''])[0]
            if self.item.seller:
                data['seller_name'] = self.item.seller.username
        if self.buyer:
            data['buyer'] = self.buyer.to_dict()
            data['buyer_name'] = self.buyer.username
        return data


class UserAction(db.Model):
    __tablename__ = 'user_actions'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)  # BigSerial
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    action_type = db.Column(db.String(20), nullable=False)  # view, fav, search
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'item_id': self.item_id,
            'action_type': self.action_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ==================== 辅助表（支撑现有功能） ====================

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    msg_type = db.Column(db.String(20), default='text')
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'content': self.content,
            'type': self.msg_type,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sender': self.sender.to_dict() if self.sender else None
        }


class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(500))
    image = db.Column(db.String(256))
    used_count = db.Column(db.Integer, default=0)
    rating = db.Column(db.Numeric(2, 1), default=5.0)
    distance = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image': self.image,
            'usedCount': self.used_count,
            'rating': float(self.rating) if self.rating else 5.0,
            'distance': self.distance,
        }


class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    __table_args__ = (db.UniqueConstraint('user_id', 'item_id', name='uq_cart_user_item'),)

    def to_dict(self):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'item_id': self.item_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if self.item:
            data['item'] = self.item.to_dict(include_seller=True)
        return data


class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(10), default='info')
    module = db.Column(db.String(64))
    action = db.Column(db.String(128))
    detail = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.now)

    operator = db.relationship('User', backref='logs')

    def to_dict(self):
        return {
            'id': self.id,
            'level': self.level,
            'module': self.module,
            'action': self.action,
            'detail': self.detail,
            'user_id': self.user_id,
            'username': self.operator.username if self.operator else None,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class StudentVerification(db.Model):
    """虚拟学信网数据库 - 用于验证学生身份"""
    __tablename__ = 'student_verifications'
    id = db.Column(db.Integer, primary_key=True)
    school_name = db.Column(db.String(128), nullable=False, index=True)
    student_id = db.Column(db.String(32), nullable=False, index=True)
    real_name = db.Column(db.String(64), nullable=False)

    __table_args__ = (db.UniqueConstraint('school_name', 'student_id', name='uq_school_student'),)

    def to_dict(self):
        return {
            'id': self.id,
            'school_name': self.school_name,
            'student_id': self.student_id,
            'real_name': self.real_name,
        }


# ==================== 推荐系统表 ====================

class ItemEmbedding(db.Model):
    """商品 TF-IDF 向量缓存"""
    __tablename__ = 'item_embeddings'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False, unique=True)
    embedding = db.Column(ARRAY(db.Float), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    item = db.relationship('Item', backref=db.backref('embedding_record', uselist=False))

    def to_dict(self):
        return {
            'id': self.id,
            'item_id': self.item_id,
            'embedding': self.embedding,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserInterest(db.Model):
    """用户兴趣标签（高频浏览类别）"""
    __tablename__ = 'user_interests'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(UUID(as_uuid=True), db.ForeignKey('categories.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    __table_args__ = (db.UniqueConstraint('user_id', 'category_id', name='uq_user_interest'),)

    user_ref = db.relationship('User', backref='interests')
    category = db.relationship('Category')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': str(self.category_id),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    app_type = db.Column(db.String(20), nullable=False)  # category, location
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    reject_reason = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.now)

    applicant = db.relationship('User', backref='applications')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.applicant.username if self.applicant else None,
            'app_type': self.app_type,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'reject_reason': self.reject_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ==================== 风控系统表 ====================

class RiskLog(db.Model):
    """风控行为日志"""
    __tablename__ = 'risk_logs'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action_type = db.Column(db.String(32), nullable=False)  # review, price_change, keyword, etc.
    target_id = db.Column(db.Integer)  # item_id or order_id
    ip_address = db.Column(db.String(45))
    device_id = db.Column(db.String(128))
    content = db.Column(db.Text)
    risk_score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)

    user = db.relationship('User', backref='risk_logs')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action_type': self.action_type,
            'target_id': self.target_id,
            'ip_address': self.ip_address,
            'device_id': self.device_id,
            'content': self.content,
            'risk_score': self.risk_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserRiskTag(db.Model):
    """用户风险标签"""
    __tablename__ = 'user_risk_tags'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    tag_type = db.Column(db.String(32), nullable=False)  # frequent_review, price_abuse, keyword_violation
    severity = db.Column(db.String(16), default='low')  # low, medium, high
    detail = db.Column(db.Text)
    auto_tagged = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    expires_at = db.Column(db.DateTime)

    user = db.relationship('User', backref='risk_tags')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'tag_type': self.tag_type,
            'severity': self.severity,
            'detail': self.detail,
            'auto_tagged': self.auto_tagged,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }


# ==================== 公告系统表 ====================

class Banner(db.Model):
    """首页轮播图"""
    __tablename__ = 'banners'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    tag = db.Column(db.String(20))  # 标签文字，如"限时活动"
    description = db.Column(db.String(200))
    image = db.Column(db.String(500))  # 背景图片URL
    bg_color = db.Column(db.String(200))  # 渐变背景色
    emoji = db.Column(db.String(10))  # 装饰emoji
    link = db.Column(db.String(200))  # 跳转链接
    sort_order = db.Column(db.Integer, default=0)  # 排序
    status = db.Column(db.String(20), default='draft')  # draft, published, archived
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'tag': self.tag,
            'description': self.description,
            'image': self.image,
            'bg_color': self.bg_color,
            'bg': self.bg_color,  # 兼容前端
            'emoji': self.emoji,
            'link': self.link,
            'sort_order': self.sort_order,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Announcement(db.Model):
    """平台公告"""
    __tablename__ = 'announcements'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    status = db.Column(db.String(20), default='draft')  # draft, published, archived
    publisher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    publish_time = db.Column(db.DateTime)
    expire_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    publisher = db.relationship('User', backref='announcements')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'priority': self.priority,
            'status': self.status,
            'publisher_id': self.publisher_id,
            'publisher_name': self.publisher.username if self.publisher else None,
            'publish_time': self.publish_time.isoformat() if self.publish_time else None,
            'expire_time': self.expire_time.isoformat() if self.expire_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# ==================== 举报与申诉系统表 ====================

class Report(db.Model):
    """举报记录"""
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    report_type = db.Column(db.String(20), nullable=False)  # user, item, review, order
    target_id = db.Column(db.Integer, nullable=False)  # 被举报对象ID
    reason = db.Column(db.String(50), nullable=False)  # fraud, spam, inappropriate, fake, other
    description = db.Column(db.Text)
    evidence_images = db.Column(ARRAY(db.String))  # 证据图片
    status = db.Column(db.String(20), default='pending')  # pending, processing, resolved, rejected
    handler_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    handle_result = db.Column(db.Text)
    handle_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now)

    reporter = db.relationship('User', foreign_keys=[reporter_id], backref='reports_submitted')
    handler = db.relationship('User', foreign_keys=[handler_id], backref='reports_handled')

    def to_dict(self):
        return {
            'id': self.id,
            'reporter_id': self.reporter_id,
            'reporter_name': self.reporter.username if self.reporter else None,
            'report_type': self.report_type,
            'target_id': self.target_id,
            'reason': self.reason,
            'description': self.description,
            'evidence_images': self.evidence_images or [],
            'status': self.status,
            'handler_id': self.handler_id,
            'handler_name': self.handler.username if self.handler else None,
            'handle_result': self.handle_result,
            'handle_time': self.handle_time.isoformat() if self.handle_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Appeal(db.Model):
    """申诉记录"""
    __tablename__ = 'appeals'
    id = db.Column(db.Integer, primary_key=True)
    appellant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    appeal_type = db.Column(db.String(20), nullable=False)  # order, review, ban, item
    target_id = db.Column(db.Integer, nullable=False)  # 申诉对象ID
    reason = db.Column(db.Text, nullable=False)
    evidence_images = db.Column(ARRAY(db.String))
    status = db.Column(db.String(20), default='pending')  # pending, processing, approved, rejected
    handler_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    handle_result = db.Column(db.Text)
    handle_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now)

    appellant = db.relationship('User', foreign_keys=[appellant_id], backref='appeals_submitted')
    handler = db.relationship('User', foreign_keys=[handler_id], backref='appeals_handled')

    def to_dict(self):
        return {
            'id': self.id,
            'appellant_id': self.appellant_id,
            'appellant_name': self.appellant.username if self.appellant else None,
            'appeal_type': self.appeal_type,
            'target_id': self.target_id,
            'reason': self.reason,
            'evidence_images': self.evidence_images or [],
            'status': self.status,
            'handler_id': self.handler_id,
            'handler_name': self.handler.username if self.handler else None,
            'handle_result': self.handle_result,
            'handle_time': self.handle_time.isoformat() if self.handle_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ==================== 评价系统表 ====================

class Review(db.Model):
    """交易评价"""
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(UUID(as_uuid=True), db.ForeignKey('orders.id'), nullable=True)  # 回复时可为空
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reviewed_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 回复时可为空
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=True)  # 1-5星，回复时可为空
    content = db.Column(db.Text)
    review_type = db.Column(db.String(16), nullable=True)  # buyer_to_seller, seller_to_buyer, reply
    is_anonymous = db.Column(db.Boolean, default=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('reviews.id'), nullable=True)  # 回复的父评价ID
    created_at = db.Column(db.DateTime, default=datetime.now)

    order = db.relationship('Order', backref='reviews')
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='reviews_given')
    reviewed_user = db.relationship('User', foreign_keys=[reviewed_user_id], backref='reviews_received')
    item = db.relationship('Item', backref='reviews')
    replies = db.relationship('Review', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')

    def to_dict(self, include_replies=False):
        data = {
            'id': self.id,
            'order_id': str(self.order_id) if self.order_id else None,
            'reviewer_id': self.reviewer_id,
            'reviewed_user_id': self.reviewed_user_id,
            'item_id': self.item_id,
            'rating': self.rating,
            'content': self.content,
            'review_type': self.review_type,
            'is_anonymous': self.is_anonymous,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'reviewer': None,
            'item': None
        }
        try:
            if self.reviewer:
                data['reviewer'] = {
                    'id': self.reviewer.id,
                    'username': '匿名用户' if self.is_anonymous else self.reviewer.username
                }
        except Exception:
            pass
        try:
            if self.item:
                data['item'] = {'id': self.item.id, 'name': self.item.name}
        except Exception:
            pass
        if include_replies:
            try:
                data['replies'] = [r.to_dict() for r in self.replies.order_by(Review.created_at.asc()).all()]
            except Exception:
                data['replies'] = []
        return data



