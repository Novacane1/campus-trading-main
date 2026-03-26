import os
import html
from flask import Blueprint, request, jsonify, current_app
import json
import requests as http_requests
from app.models.models import Item, UserAction, Category, User
from app import db, redis_client
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

items_bp = Blueprint('items', __name__)


def log_action(user_id, item_id, action_type):
    # 浏览行为去重：同一用户+商品 5分钟内不重复记录
    if action_type == 'view':
        recent = UserAction.query.filter_by(
            user_id=user_id, item_id=item_id, action_type='view'
        ).order_by(UserAction.created_at.desc()).first()
        if recent and recent.created_at and \
           (datetime.now() - recent.created_at) < timedelta(minutes=5):
            return False  # 跳过重复浏览
    action = UserAction(user_id=user_id, item_id=item_id, action_type=action_type)
    db.session.add(action)
    db.session.commit()
    return True


def invalidate_recommendation_cache(user_id):
    """用户行为变化后，主动失效个性化推荐缓存。"""
    try:
        if redis_client:
            redis_client.delete(f'rec:user:{user_id}')
    except Exception:
        pass


def sanitize_text(value, max_len=None):
    """Basic XSS-safe sanitization for user-provided text fields."""
    if value is None:
        return None
    text = str(value).strip()
    if max_len is not None:
        text = text[:max_len]
    # Escape HTML tags to prevent script injection storage/rendering.
    return html.escape(text, quote=False)


# 搜索同义词/关键词扩展表 —— 每组关键词互不交叉，避免跨类污染
SEARCH_SYNONYMS = {
    # ── 数码电子 ──
    '电脑': ['笔记本电脑', 'laptop', 'MacBook', 'ThinkPad', '联想电脑',
             '戴尔电脑', 'Dell', '华硕电脑', 'ASUS', '惠普电脑', 'Surface',
             '台式机', '一体机', 'iMac', '小新', '拯救者', 'ROG', '外星人',
             '游戏本', '轻薄本', 'Mac mini', '组装机', '迷你主机',
             '电脑配件', '笔记本支架', '扩展坞'],
    '手机': ['iPhone', '苹果手机', '华为手机', 'Huawei', '小米手机', 'Xiaomi',
             'OPPO', 'vivo', '三星', 'Samsung', 'OnePlus', '一加', 'Redmi',
             '红米', '荣耀', 'Honor', 'Pixel', '魅族', 'realme', '手机壳',
             '手机膜', '钢化膜', 'iqoo', '中兴', 'Nothing', '手机支架'],
    '平板': ['iPad', 'iPad Pro', 'iPad Air', 'iPad mini', 'tablet',
             '华为平板', 'MatePad', 'Surface Pro', '小米平板', '平板电脑',
             '触控笔', 'Apple Pencil', '手写笔', '平板支架', '平板键盘'],
    '耳机': ['AirPods', 'AirPods Pro', '蓝牙耳机', '无线耳机', '头戴式耳机',
             '入耳式耳机', 'Beats', 'Sony耳机', '索尼耳机', 'JBL耳机',
             '降噪耳机', 'TWS', '有线耳机', '游戏耳机', '监听耳机',
             'Bose耳机', '森海塞尔', '铁三角', '漫步者', '华为耳机',
             'FreeBuds', '骨传导耳机', 'Galaxy Buds', '耳机套'],
    '键盘': ['keyboard', '机械键盘', 'cherry', 'HHKB', 'Filco', '薄膜键盘',
             '无线键盘', '客制化键盘', '电竞键盘', 'Keychron', 'Leopold',
             '达尔优键盘', '雷柏', 'ikbc', 'RK', '键帽',
             '矮轴键盘', '蓝牙键盘', 'NuPhy', 'Lofree'],
    '鼠标': ['mouse', '罗技鼠标', 'Logitech', '雷蛇', 'Razer', '无线鼠标',
             '游戏鼠标', '蓝牙鼠标', '双飞燕', '卓威', '达尔优鼠标',
             '鼠标垫', '静音鼠标', '竖握鼠标', '轨迹球'],
    '相机': ['单反', '微单', 'Canon', '佳能', 'Nikon', '尼康', '富士', 'Fuji',
             'GoPro', '摄影', '镜头', '索尼相机', '卡片机', '拍立得',
             '胶片机', '运动相机', '三脚架', '稳定器', 'DJI', '大疆',
             '补光灯', '滤镜', '相机包', 'Insta360', 'vlog相机'],
    '显示器': ['显示屏', '曲面屏', '电竞显示器', '4K显示器', '2K显示器',
               'monitor', '便携屏', '带鱼屏', '高刷显示器',
               '显示器支架', '屏幕挂灯'],
    '音响': ['音箱', '蓝牙音箱', 'JBL音箱', 'Bose音箱', 'Marshall', '便携音箱',
             '桌面音箱', '低音炮', 'Soundbar', 'Harman', '哈曼卡顿',
             '漫步者音箱', '小度', '天猫精灵', '小爱同学', '智能音箱'],
    '手表': ['智能手表', 'Apple Watch', '小米手环', '华为手环', '运动手表',
             '机械表', '石英表', 'Garmin', '佳明', '华为手表', '电子表',
             'CASIO', '卡西欧', 'G-Shock', 'DW', '运动手环', '华米'],
    '充电': ['充电宝', '充电器', '数据线', '移动电源', 'Type-C', 'Lightning',
             '快充头', '无线充电器', 'Anker', '紫米', '倍思',
             'MagSafe', '氮化镓充电器', 'GaN', '插线板', '排插',
             '车载充电器', 'USB-C'],
    '存储': ['U盘', '硬盘', '移动硬盘', 'SSD', '固态硬盘', '内存卡', 'SD卡',
             'TF卡', '机械硬盘', '闪存盘', 'NAS', '内存条', '硬盘盒',
             '读卡器'],
    '游戏': ['PS5', 'PS4', 'Switch', 'Nintendo', '任天堂', 'Xbox', '游戏机',
             '手柄', 'Joy-Con', '游戏卡带', 'Steam Deck', '掌机', 'NS',
             'PSP', 'PSV', '游戏碟', '街机', '摇杆', 'Pro手柄', 'Amiibo'],
    '网络设备': ['路由器', 'WiFi', '网线', '交换机', '网卡', '无线网卡',
                 '信号放大器', 'WiFi6', '随身WiFi', 'mesh', '光猫'],
    '投影仪': ['投影', '便携投影', '家用投影', '投影幕布', '幕布',
               '微投', '激光投影', '当贝', '极米', '坚果投影'],
    '打印机': ['打印', '复印机', '扫描仪', '墨盒', '硒鼓',
               '喷墨打印', '激光打印', '照片打印机', '错题打印机'],

    # ── 图书教材 ──
    '教材': ['课本', '教科书', '参考书', '习题集', '考研资料', '辅导书',
             '真题', '试卷', '复习资料', '学习资料', '练习册', '题库',
             '高数', '线代', '概率论', '大学物理', '四六级', '雅思',
             '托福', 'GRE', '考公资料', 'CPA', 'CFA', '注会',
             '司考', '法考', '考研英语', '考研政治', '考研数学',
             '专升本', '期末资料', '复习笔记',
             '张宇', '汤家凤', '李永乐', '肖秀荣', '王道', '408'],
    '书': ['书籍', '小说', '图书', '文学', '漫画', '杂志', '绘本', '传记',
           '名著', '读物', '散文集', '诗集', '工具书', '词典', '字典',
           '科幻', '推理', '悬疑', '言情', '武侠', '历史书', '哲学书',
           '心理学', '经济学', '画册', '英文原版', '外文书'],
    '编程书': ['编程', 'Python书', 'Java书', 'C++', '算法书',
               '数据结构', '计算机网络', '操作系统', '数据库',
               '机器学习', '深度学习', 'AI', '人工智能', '设计模式'],

    # ── 服装（各组独立、不交叉） ──
    '衣服': ['外套', '卫衣', 'T恤', '裤子', '裙子', '羽绒服', '衬衫',
             '牛仔裤', '棉服', '大衣', '毛衣', 'polo衫', '短袖', '长袖',
             '连衣裙', '夹克', '风衣', '西装', '校服', '汉服', 'JK制服',
             '卫裤', '运动裤', '休闲裤', '短裤', '工装裤', '阔腿裤',
             '半身裙', '百褶裙', '针织衫', '马甲', '背心', '冲锋衣',
             '防晒衣', '棉袄', '睡衣', '内衣', '秋衣秋裤'],
    '鞋': ['鞋子', '球鞋', '跑鞋', '运动鞋', '帆布鞋', '靴子', '板鞋',
           '凉鞋', '拖鞋', '马丁靴', '休闲鞋', '小白鞋', '高跟鞋', '皮鞋',
           'AJ', 'Air Jordan', 'Air Force', 'Yeezy', 'Nike鞋', 'Adidas鞋',
           '匡威', 'Converse', 'Vans', 'New Balance', 'NB',
           '雪地靴', 'UGG', '乐福鞋', '豆豆鞋', '增高鞋', '德训鞋',
           '洞洞鞋', 'Crocs', '老爹鞋', '篮球鞋', '足球鞋'],
    '包': ['书包', '背包', '双肩包', '挎包', '行李箱', '旅行箱', '手提包',
           '钱包', '卡包', '腰包', '单肩包', '斜挎包', '帆布包', '电脑包',
           '拉杆箱', '收纳袋', '旅行包', '登山包', '胸包'],
    '配饰': ['帽子', '围巾', '手套', '腰带', '皮带', '领带', '袜子',
             '墨镜', '太阳镜', '眼镜', '近视眼镜', '发箍', '发卡',
             '耳环', '项链', '手链', '戒指', '胸针', '头绳'],

    # ── 运动器材（不包含鞋和衣服） ──
    '运动': ['篮球', '足球', '羽毛球', '乒乓球', '网球', '排球', '瑜伽垫',
             '健身器材', '哑铃', '羽毛球拍', '乒乓球拍', '网球拍',
             '跳绳', '拉力带', '瑜伽', '滑板', '轮滑', '护膝', '护腕',
             '泳镜', '泳帽', '壶铃', '弹力带', '握力器', '臂力器',
             '仰卧板', '引体向上器', '筋膜枪', '计数器', '运动护具',
             '棒球', '高尔夫', '飞盘', '拳击手套', '跆拳道护具'],
    '自行车': ['单车', '山地车', '公路车', '骑行', '折叠车', '头盔', '车灯',
               '死飞', '骑行手套', '自行车锁', '车筐', '后座', '骑行服'],
    '户外': ['帐篷', '睡袋', '登山杖', '户外装备', '露营',
             '野餐垫', '水壶', '指南针', '望远镜', '手电筒',
             '折叠椅', '炉具', '防潮垫', '钓鱼竿', '鱼竿'],

    # ── 生活用品 ──
    '家电': ['电风扇', '台灯', '吹风机', '电热水壶', '加湿器', '小家电',
             '电饭煲', '微波炉', '榨汁机', '电暖器', '暖手宝', '烧水壶',
             '热水袋', '迷你冰箱', '挂烫机', '空气净化器',
             '除湿机', '电熨斗', '养生壶', '豆浆机', '空气炸锅',
             '电磁炉', '破壁机', '酸奶机', '烤箱', '小冰箱'],
    '文具': ['本子', '铅笔', '钢笔', '尺子', '计算器',
             '马克笔', '荧光笔', '便利贴', '文件夹', '订书机', '修正带',
             '手账本', '水彩笔', '彩铅', '素描本', '画板', '颜料',
             '毛笔', '墨水', '橡皮', '圆规', '三角板', '涂改液',
             '笔袋', '文具盒'],
    '化妆品': ['护肤品', '面膜', '口红', '粉底', '香水', '美妆', '洗面奶',
               '水乳', '精华', '防晒霜', '眼影', '腮红', '卸妆', '化妆刷',
               '眉笔', '睫毛膏', '散粉', '遮瑕', '唇釉', '唇膏',
               '定妆喷雾', '美瞳', '假睫毛', '化妆镜', '化妆包',
               '身体乳', '护手霜', '面霜', '爽肤水', '卸妆水'],
    '日用品': ['洗衣液', '牙膏', '牙刷', '毛巾', '浴巾', '衣架', '收纳盒',
               '纸巾', '洗发水', '沐浴露', '梳子', '镜子', '雨伞',
               '保鲜盒', '垃圾袋', '晾衣架', '拖把', '抹布',
               '洗洁精', '消毒液', '香薰', '蜡烛', '驱蚊液'],
    '乐器': ['吉他', '尤克里里', '钢琴', '电子琴', '口琴', '笛子',
             '小提琴', '架子鼓', '古筝', '二胡', '电吉他', '贝斯',
             '萨克斯', '长笛', '琴弦', '琴包', '节拍器', '调音器',
             '吉他拨片', '卡林巴'],
    '宿舍': ['床上用品', '被子', '枕头', '床单', '被套', '凉席', '蚊帐',
             '床帘', '置物架', '桌面收纳', '挂钩', '夜灯', '小夜灯',
             '插排', '收纳箱', '鞋架', '脏衣篓', '垃圾桶',
             '桌面风扇', '床头灯', '门帘'],
    '厨具': ['锅', '碗', '盘子', '筷子', '勺子', '杯子', '水杯',
             '保温杯', '马克杯', '饭盒', '便当盒', '菜板', '刀具',
             '开瓶器', '保鲜膜', '烘焙工具', '咖啡杯', '茶具'],

    # ── 考试学习工具 ──
    '考试': ['考研', '四级', '六级', 'CET4', 'CET6', '英语四级', '英语六级',
             '专四', '专八', '计算机二级', '计算机三级', '教资',
             '教师资格证', '普通话考试', '驾照', '科目一', '科目四',
             '初级会计', '证券从业', '基金从业', '银行从业'],

    # ── 代步出行 ──
    '出行': ['电动车', '滑板车', '电瓶车', '电动自行车', '代步车',
             '平衡车', '电动滑板车', '九号', '小牛电动', '雅迪', '爱玛'],

    # ── 食品零食 ──
    '零食': ['零食', '饮料', '咖啡', '茶叶', '奶茶', '方便面', '速食',
             '坚果', '饼干', '巧克力', '糖果', '薯片', '辣条',
             '水果', '牛奶', '酸奶'],

}

# ── 大类聚合（仅单向展开：搜"数码"→展开到子类，但搜"手机"不会反向拉入整个数码组） ──
SEARCH_CATEGORIES = {
    '数码': ['电脑', '手机', '平板', '耳机', '相机', '充电宝', '智能手表',
             '显示器', '键盘', '鼠标', '音箱', '数据线', '充电器',
             '路由器', '投影仪', '打印机', '网络设备'],
    '服装': ['衣服', '裤子', '裙子', '外套', '卫衣', 'T恤', '羽绒服',
             '衬衫', '毛衣', '连衣裙', '牛仔裤', '鞋子', '包', '配饰',
             '帽子', '围巾'],
    '图书': ['教材', '课本', '小说', '参考书', '书籍', '漫画', '杂志',
             '考研资料', '真题', '辅导书', '文学', '传记', '编程书',
             '英文原版'],
    '生活': ['日用品', '家电', '文具', '化妆品', '收纳', '床上用品', '台灯',
             '宿舍', '厨具', '乐器', '零食'],
    '学习': ['教材', '文具', '考试', '考研', '四六级', '计算器', '笔记本',
             '便利贴', '台灯', '平板', 'iPad'],
}


def expand_search_keywords(query_str):
    """将搜索词扩展为包含同义词的关键词列表。
    仅做精确匹配（大小写不敏感），避免子字符串匹配导致的跨类污染。

    SEARCH_SYNONYMS —— 双向匹配：搜词命中 key 或 synonym 都展开整组。
    SEARCH_CATEGORIES —— 单向匹配：仅搜词与 key 精确匹配时才展开，
                         避免搜"手机"反向拉入整个"数码"组。

    例：输入"电脑" → 返回 ["电脑", "笔记本", "MacBook", "ThinkPad", ...]
    例：输入"手机" → 返回 ["手机", "iPhone", "华为手机", ...]（不含电脑、平板）
    例：输入"数码" → 返回 ["数码", "电脑", "手机", "平板", "耳机", ...]
    """
    keywords = {query_str}
    q_lower = query_str.strip().lower()

    # 1. SEARCH_SYNONYMS：双向匹配（搜词 ↔ key/synonym）
    for key, synonyms in SEARCH_SYNONYMS.items():
        matched = False
        if q_lower == key.lower():
            matched = True
        if not matched:
            for syn in synonyms:
                if q_lower == syn.lower():
                    matched = True
                    break
        if matched:
            keywords.update(synonyms)
            keywords.add(key)

    # 2. SEARCH_CATEGORIES：单向匹配（仅搜词 == key 时展开）
    for key, sub_keywords in SEARCH_CATEGORIES.items():
        if q_lower == key.lower():
            keywords.update(sub_keywords)
            keywords.add(key)

    return list(keywords)


@items_bp.route('/', methods=['GET'])
@items_bp.route('/search', methods=['GET'])
@jwt_required(optional=True)
def get_items():
    current_user_id = get_jwt_identity()
    category_id = request.args.get('category_id')
    search_query = request.args.get('q') or request.args.get('keyword')
    seller_id = request.args.get('seller_id')
    status = request.args.get('status')

    # 校园隔离：登录用户且有学校信息时，只返回同校商品
    current_user = User.query.get(current_user_id) if current_user_id else None
    current_school = current_user.school_name if current_user else None

    # 基础查询
    if seller_id:
        query = Item.query.filter_by(seller_id=seller_id)
    else:
        query = Item.query

    # 校园隔离过滤（使用子查询避免与后续 JOIN 冲突）
    if current_school:
        same_school_seller_ids = db.session.query(User.id).filter(User.school_name == current_school).subquery()
        query = query.filter(Item.seller_id.in_(db.session.query(same_school_seller_ids)))

    # 状态过滤
    if status and status != 'all':
        status_map = {'available': 'on_sale', 'reserved': 'reserved'}
        query = query.filter_by(status=status_map.get(status, status))
    else:
        # 默认不显示已删除和已售出的商品
        query = query.filter(Item.status.notin_(['deleted', 'sold']))

    if category_id:
        query = query.filter_by(category_id=category_id)
    if search_query:
        search_terms = expand_search_keywords(search_query)
        conditions = []
        for term in search_terms:
            # 所有展开词只匹配商品名称，避免描述中偶然提及导致误匹配
            # 例：搜"电脑"不应命中描述含"可放电脑"的折叠桌/背包
            conditions.append(Item.name.ilike(f'%{term}%'))
        # 也匹配分类名称
        conditions.append(Item.category.has(Category.name.ilike(f'%{search_query}%')))
        query = query.filter(db.or_(*conditions))

    # 价格区间筛选
    price_range = request.args.get('price_range')
    if price_range:
        parts = price_range.split('-')
        if len(parts) == 2:
            min_price, max_price = parts
            if min_price:
                query = query.filter(Item.price >= float(min_price))
            if max_price:
                query = query.filter(Item.price <= float(max_price))

    # 交易地点筛选
    location_filter = request.args.get('location')
    if location_filter:
        query = query.filter(Item.location == location_filter)

    # 商品成色筛选
    condition_filter = request.args.get('condition')
    if condition_filter:
        query = query.filter(Item.condition == condition_filter)

    # 发布时间筛选
    time_range = request.args.get('time_range')
    if time_range:
        try:
            days = int(time_range)
            since = datetime.now() - timedelta(days=days)
            query = query.filter(Item.created_at >= since)
        except (ValueError, TypeError):
            pass

    # 排序
    sort = request.args.get('sort', 'latest')
    if sort == 'price_asc':
        query = query.order_by(Item.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Item.price.desc())
    elif sort == 'popular':
        query = query.outerjoin(UserAction, (UserAction.item_id == Item.id) & (UserAction.action_type == 'view')) \
                     .group_by(Item.id) \
                     .order_by(db.func.count(UserAction.id).desc(), Item.created_at.desc())
    else:
        query = query.order_by(Item.created_at.desc())

    # 总数（分页前）
    total = query.count()

    # 分页
    page = request.args.get('page', 1, type=int)
    per_page_arg = request.args.get('per_page')
    limit_arg = request.args.get('limit')
    
    if per_page_arg:
        per_page = int(per_page_arg)
    elif limit_arg:
        per_page = int(limit_arg)
    else:
        per_page = 20

    offset = (page - 1) * per_page
    items = query.offset(offset).limit(per_page).all()
    pages = (total + per_page - 1) // per_page if per_page > 0 else 1

    # 构建响应
    result = {
        'items': [item.to_dict(include_seller=True) for item in items],
        'products': [item.to_dict(include_seller=True) for item in items],
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': pages
    }

    # 如果按分类筛选，返回分类名称
    if category_id:
        cat = Category.query.get(category_id)
        if cat:
            result['category_name'] = cat.name

    return jsonify(result), 200


@items_bp.route('/<int:item_id>', methods=['GET'])
@jwt_required(optional=True)
def get_item_detail(item_id):
    item = Item.query.get_or_404(item_id)

    return jsonify(item.to_dict(include_seller=True)), 200


@items_bp.route('/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_item(item_id):
    user_id = get_jwt_identity()
    item = Item.query.get_or_404(item_id)
    if str(item.seller_id) != str(user_id):
        return jsonify({'msg': 'Forbidden'}), 403
    item.status = 'deleted'
    db.session.commit()
    return jsonify({'msg': 'Deleted'}), 200


@items_bp.route('/publish', methods=['POST'])
@jwt_required()
def publish_item():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.can_publish is False:
        return jsonify({'msg': '您已被禁止发布商品，请联系管理员'}), 403
    name = None
    category_id = None
    description = None
    price = None
    condition = None
    location = None
    quantity = 1
    images = []
    available_time_slots = []
    preferred_locations = []

    if request.is_json:
        data = request.get_json() or {}
        name = sanitize_text(data.get('name') or data.get('title'), max_len=128)
        category_id = data.get('category_id')
        description = sanitize_text(data.get('description'), max_len=5000)
        price = data.get('price')
        condition = sanitize_text(data.get('condition'), max_len=20)
        location = sanitize_text(data.get('location'), max_len=128)
        quantity = data.get('quantity', 1)
        images = data.get('images') or []
        available_time_slots = data.get('available_time_slots') or []
        preferred_locations = data.get('preferred_locations') or []
    else:
        name = sanitize_text(request.form.get('name'), max_len=128)
        category_id = request.form.get('category_id')
        description = sanitize_text(request.form.get('description'), max_len=5000)
        price = request.form.get('price')
        condition = sanitize_text(request.form.get('condition'), max_len=20)
        location = sanitize_text(request.form.get('location'), max_len=128)
        quantity = int(request.form.get('quantity', 1))
        img_str = request.form.get('images')
        if img_str:
            try:
                images = json.loads(img_str)
            except Exception:
                images = []
        time_slots_str = request.form.get('available_time_slots')
        if time_slots_str:
            try:
                available_time_slots = json.loads(time_slots_str)
            except Exception:
                available_time_slots = []
        locations_str = request.form.get('preferred_locations')
        if locations_str:
            try:
                preferred_locations = json.loads(locations_str)
            except Exception:
                preferred_locations = []

    if not all([name, category_id, price]):
        return jsonify({'msg': 'Missing required fields'}), 400

    image_file = request.files.get('image')
    if image_file:
        filename = secure_filename(f"{datetime.now().timestamp()}_{image_file.filename}")
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        image_file.save(image_path)
        images = [f"/static/uploads/{filename}"]

    # 确保数量至少为1
    if quantity is None or quantity < 1:
        quantity = 1

    item = Item(
        seller_id=user_id,
        category_id=category_id,
        name=name,
        description=description,
        price=price,
        condition=condition,
        location=location,
        quantity=quantity,
        images=images or None,
        available_time_slots=available_time_slots if available_time_slots else None,
        preferred_locations=preferred_locations if preferred_locations else None
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201


@items_bp.route('/ranking/popular', methods=['GET'])
@jwt_required(optional=True)
def get_popular_items():
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id) if current_user_id else None
    current_school = current_user.school_name if current_user else None

    top_items_ids = []
    try:
        if redis_client:
            top_items_ids = redis_client.zrevrange('item_views', 0, 9)
    except Exception:
        pass
    if not top_items_ids:
        query = Item.query.filter_by(status='on_sale')
        if current_school:
            query = query.join(User, Item.seller_id == User.id).filter(User.school_name == current_school)
        items = query.order_by(Item.created_at.desc()).limit(10).all()
        return jsonify([item.to_dict(include_seller=True) for item in items]), 200
    items = Item.query.filter(Item.id.in_([int(x) for x in top_items_ids])).all()
    # 校园隔离过滤
    if current_school:
        items = [i for i in items if i.seller and i.seller.school_name == current_school]
    items_dict = {str(item.id): item for item in items}
    sorted_items = [items_dict[str(item_id)].to_dict(include_seller=True) for item_id in top_items_ids if str(item_id) in items_dict]
    return jsonify(sorted_items), 200


@items_bp.route('/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_item(item_id):
    user_id = get_jwt_identity()
    item = Item.query.get_or_404(item_id)
    if str(item.seller_id) != str(user_id):
        return jsonify({'msg': 'Forbidden'}), 403
    data = request.get_json() or {}
    if 'name' in data or 'title' in data:
        item.name = sanitize_text(data.get('name') or data.get('title'), max_len=128)
    if 'description' in data:
        item.description = sanitize_text(data['description'], max_len=5000)
    if 'price' in data:
        item.price = data['price']
    if 'category_id' in data:
        item.category_id = data['category_id']
    if 'condition' in data:
        item.condition = sanitize_text(data['condition'], max_len=20)
    if 'location' in data:
        item.location = sanitize_text(data['location'], max_len=128)
    if 'images' in data:
        item.images = data['images']
    db.session.commit()
    return jsonify(item.to_dict(include_seller=True)), 200


@items_bp.route('/<int:item_id>/off-shelf', methods=['PUT'])
@jwt_required()
def off_shelf_item(item_id):
    user_id = get_jwt_identity()
    item = Item.query.get_or_404(item_id)
    if str(item.seller_id) != str(user_id):
        return jsonify({'msg': 'Forbidden'}), 403
    item.status = 'locked'
    db.session.commit()
    return jsonify({'msg': 'Item taken off shelf'}), 200


@items_bp.route('/<int:item_id>/favorite', methods=['POST'])
@jwt_required()
def favorite_item(item_id):
    user_id = get_jwt_identity()
    Item.query.get_or_404(item_id)
    existing = UserAction.query.filter_by(
        user_id=user_id, item_id=item_id, action_type='fav'
    ).first()
    if existing:
        return jsonify({'msg': 'Already favorited'}), 200
    action = UserAction(user_id=user_id, item_id=item_id, action_type='fav')
    db.session.add(action)
    db.session.commit()
    invalidate_recommendation_cache(user_id)
    return jsonify({'msg': 'Favorited'}), 201


@items_bp.route('/<int:item_id>/favorite', methods=['DELETE'])
@jwt_required()
def unfavorite_item(item_id):
    user_id = get_jwt_identity()
    action = UserAction.query.filter_by(
        user_id=user_id, item_id=item_id, action_type='fav'
    ).first()
    if action:
        db.session.delete(action)
        db.session.commit()
        invalidate_recommendation_cache(user_id)
    return jsonify({'msg': 'Unfavorited'}), 200


@items_bp.route('/favorites', methods=['GET'])
@jwt_required()
def get_favorites():
    user_id = get_jwt_identity()
    actions = UserAction.query.filter_by(user_id=user_id, action_type='fav').all()
    item_ids = [a.item_id for a in actions]
    items = Item.query.filter(Item.id.in_(item_ids)).all()
    return jsonify({'products': [item.to_dict(include_seller=True) for item in items]}), 200


@items_bp.route('/<int:item_id>/view', methods=['POST'])
@jwt_required()
def record_view(item_id):
    user_id = get_jwt_identity()
    Item.query.get_or_404(item_id)
    inserted = log_action(user_id, item_id, 'view')
    if inserted:
        invalidate_recommendation_cache(user_id)
    try:
        if redis_client:
            redis_client.zincrby('item_views', 1, item_id)
    except Exception:
        pass
    return jsonify({'msg': 'View recorded'}), 201


@items_bp.route('/history', methods=['GET'])
@jwt_required()
def get_view_history():
    user_id = get_jwt_identity()
    actions = UserAction.query.filter_by(
        user_id=user_id, action_type='view'
    ).order_by(UserAction.created_at.desc()).limit(50).all()
    item_ids = list(dict.fromkeys([a.item_id for a in actions]))
    items = Item.query.filter(Item.id.in_(item_ids)).all()
    items_map = {item.id: item for item in items}
    result = [items_map[iid].to_dict(include_seller=True) for iid in item_ids if iid in items_map]
    return jsonify({'products': result}), 200


@items_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_image():
    image_file = request.files.get('image') or request.files.get('file')
    if not image_file:
        return jsonify({'msg': 'No image file provided'}), 400

    # 先读取文件内容到内存，避免流被消耗后无法回退
    file_content = image_file.read()
    file_name = image_file.filename
    file_mimetype = image_file.mimetype

    # 尝试上传到 PicUI 图床
    picui_token = current_app.config.get('PICUI_API_TOKEN')
    if picui_token:
        try:
            resp = http_requests.post(
                'https://picui.cn/api/v1/upload',
                headers={
                    'Authorization': f'Bearer {picui_token}',
                    'Accept': 'application/json'
                },
                files={'file': (file_name, file_content, file_mimetype)},
                timeout=30
            )
            data = resp.json()
            print(f'PicUI response: {data}')
            img_data = data.get('data') or {}
            url = (img_data.get('links', {}).get('url')
                   or img_data.get('url')
                   or img_data.get('image', {}).get('url'))
            if url:
                return jsonify({'url': url}), 201
            print(f'PicUI upload failed: {data.get("message", "unknown error")}')
        except Exception as e:
            print(f'PicUI upload failed: {e}')

    # 回退到本地存储
    filename = secure_filename(f"{datetime.now().timestamp()}_{file_name}")
    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    with open(image_path, 'wb') as f:
        f.write(file_content)
    url = f"/static/uploads/{filename}"
    return jsonify({'url': url}), 201


@items_bp.route('/history', methods=['DELETE'])
@jwt_required()
def clear_view_history():
    user_id = get_jwt_identity()
    deleted = UserAction.query.filter_by(user_id=user_id, action_type='view').delete()
    db.session.commit()
    if deleted:
        invalidate_recommendation_cache(user_id)
    return jsonify({'msg': 'History cleared'}), 200


@items_bp.route('/history/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_history_item(item_id):
    user_id = get_jwt_identity()
    actions = UserAction.query.filter_by(
        user_id=user_id, item_id=item_id, action_type='view'
    ).all()
    deleted = False
    for a in actions:
        db.session.delete(a)
        deleted = True
    db.session.commit()
    if deleted:
        invalidate_recommendation_cache(user_id)
    return jsonify({'msg': 'History item deleted'}), 200

@items_bp.route('/<int:item_id>/action', methods=['POST'])
@jwt_required(optional=True)
def record_item_action(item_id):
    """记录用户行为 (浏览、收藏等)"""
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    action_type = data.get('action_type', 'view')
    item = Item.query.get_or_404(item_id)
    
    if user_id:
        from app.models.models import UserAction
        # 简单去重：同行为不要频繁记录
        recent = UserAction.query.filter_by(
            user_id=user_id, item_id=item_id, action_type=action_type
        ).order_by(UserAction.created_at.desc()).first()
        
        if not (recent and recent.created_at and (datetime.now() - recent.created_at) < timedelta(minutes=5)):
            action = UserAction(user_id=user_id, item_id=item_id, action_type=action_type)
            db.session.add(action)
            db.session.commit()
            invalidate_recommendation_cache(user_id)
            
    return jsonify({'msg': 'Action recorded'}), 200
