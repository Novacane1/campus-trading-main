"""
种子数据脚本：生成模拟用户 + 差异化行为数据。
用法：cd backend && python seed_users.py

用户偏好设计：
  user2  - 手机党：大量浏览 iPhone/小米/三星，收藏 iPhone 15
  user3  - 书虫：大量浏览考研/编程书籍，收藏算法导论
  user4  - 运动达人：浏览跑鞋/篮球/羽毛球，收藏 Nike
  user5  - 数码杂食：浏览 MacBook/iPad/耳机，收藏 AirPods
  user6  - 生活家：浏览吸尘器/电饭煲/台灯，收藏戴森
  user7  - 考研党：浏览张宇/肖秀荣/英语黄皮书
  user8  - 游戏宅：浏览 Switch/键盘/鼠标/显示器
  user9  - 文艺青年：浏览吉他/画板/水彩/三体
  user10 - 穿搭达人：浏览衣服/鞋/包
  user11 - iPad 学习党：浏览 iPad/Apple Pencil/教材
"""
import sys, os, random
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models.models import User, Item, UserAction, StudentVerification

# 用户定义：(username, school, student_id, password)
USERS = [
    ('手机达人小王', '北京大学', '2021001002', 'pass123'),
    ('书虫小李', '清华大学', '2021002001', 'pass123'),
    ('运动健将小赵', '清华大学', '2022002001', 'pass123'),
    ('数码控小钱', '复旦大学', '2021003001', 'pass123'),
    ('生活家小周', '复旦大学', '2022003001', 'pass123'),
    ('考研党小吴', '浙江大学', '2021004001', 'pass123'),
    ('游戏宅小郑', '浙江大学', '2022004001', 'pass123'),
    ('文艺青年小冯', '南京大学', '2021005001', 'pass123'),
    ('穿搭达人小陈', '南京大学', '2022005001', 'pass123'),
    ('iPad学习党小褚', '武汉大学', '2021006001', 'pass123'),
]

# 每个用户的行为偏好：关键词列表 + 收藏关键词
# (搜索关键词用于匹配商品name, 浏览次数范围, 收藏关键词)
USER_PROFILES = [
    # user2 手机党
    {
        'view_keywords': ['iPhone', '小米14', '三星Galaxy', 'iPhone 13', 'iPhone 12'],
        'view_counts': (8, 20),
        'fav_keywords': ['iPhone 15', 'iPhone 14'],
    },
    # user3 书虫
    {
        'view_keywords': ['高等数学', '线性代数', '概率论', 'Python', '算法导论', 'CSAPP', '数据结构'],
        'view_counts': (5, 15),
        'fav_keywords': ['算法导论', 'CSAPP'],
    },
    # user4 运动达人
    {
        'view_keywords': ['Nike', 'Adidas', '李宁', '篮球', '羽毛球拍', '跳绳', '哑铃'],
        'view_counts': (6, 18),
        'fav_keywords': ['Nike Air Force', 'Adidas Ultraboost'],
    },
    # user5 数码杂食
    {
        'view_keywords': ['MacBook', 'iPad', 'AirPods', 'Apple Watch', '显示器'],
        'view_counts': (5, 15),
        'fav_keywords': ['AirPods Pro', 'MacBook Pro'],
    },
    # user6 生活家
    {
        'view_keywords': ['戴森', '电饭煲', '台灯', '加湿器', '电热水壶', '空气净化'],
        'view_counts': (6, 16),
        'fav_keywords': ['戴森', '空气净化'],
    },
    # user7 考研党
    {
        'view_keywords': ['考研', '张宇', '肖秀荣', '黄皮书', '四级', '六级', '高等数学'],
        'view_counts': (8, 20),
        'fav_keywords': ['张宇', '肖秀荣'],
    },
    # user8 游戏宅
    {
        'view_keywords': ['Switch', '键盘', '鼠标', '显示器', '耳机'],
        'view_counts': (6, 18),
        'fav_keywords': ['Switch', '机械键盘'],
    },
    # user9 文艺青年
    {
        'view_keywords': ['吉他', '尤克里里', '素描', '水彩', '三体', '百年孤独', '手账'],
        'view_counts': (5, 15),
        'fav_keywords': ['吉他', '三体'],
    },
    # user10 穿搭达人
    {
        'view_keywords': ['羽绒服', '牛仔裤', '卫衣', '连衣裙', '双肩背包', '帆布鞋', '马丁靴'],
        'view_counts': (6, 16),
        'fav_keywords': ['North Face', 'Levi'],
    },
    # user11 iPad学习党
    {
        'view_keywords': ['iPad', 'Apple Pencil', '高等数学', 'Python', '台灯护眼'],
        'view_counts': (8, 20),
        'fav_keywords': ['iPad Pro', 'iPad Air'],
    },
]


def find_items_by_keywords(all_items, keywords):
    """根据关键词匹配商品"""
    matched = []
    for item in all_items:
        for kw in keywords:
            if kw.lower() in item.name.lower():
                matched.append(item)
                break
    return matched


def seed():
    app = create_app()
    with app.app_context():
        all_items = Item.query.filter_by(status='on_sale').all()
        if not all_items:
            print("没有商品数据，请先运行 seed_items.py")
            return

        print(f"找到 {len(all_items)} 个在售商品")

        # 清除旧的模拟行为数据（保留 user 1 和 5 的数据）
        existing_user_ids = [u.id for u in User.query.filter(
            User.username.in_([u[0] for u in USERS])
        ).all()]
        if existing_user_ids:
            UserAction.query.filter(
                UserAction.user_id.in_(existing_user_ids)
            ).delete(synchronize_session=False)
            db.session.commit()
            print(f"清除了 {len(existing_user_ids)} 个模拟用户的旧行为数据")

        created_users = []

        # 创建用户
        for username, school, student_id, password in USERS:
            user = User.query.filter_by(username=username).first()
            if not user:
                user = User(
                    username=username,
                    school_name=school,
                    student_id=student_id,
                )
                user.set_password(password)
                db.session.add(user)
                db.session.flush()  # 获取 id
                print(f"  创建用户: {username} (id={user.id})")
            else:
                print(f"  用户已存在: {username} (id={user.id})")
            created_users.append(user)

        db.session.commit()

        # 为每个用户生成行为数据
        now = datetime.now()
        total_actions = 0

        for i, (user, profile) in enumerate(zip(created_users, USER_PROFILES)):
            view_items = find_items_by_keywords(all_items, profile['view_keywords'])
            fav_items = find_items_by_keywords(all_items, profile['fav_keywords'])

            if not view_items:
                print(f"  {user.username}: 没有匹配到浏览商品，跳过")
                continue

            min_views, max_views = profile['view_counts']
            action_count = 0

            # 生成浏览记录
            for item in view_items:
                num_views = random.randint(min_views, max_views)
                for _ in range(num_views):
                    action = UserAction(
                        user_id=user.id,
                        item_id=item.id,
                        action_type='view',
                        created_at=now - timedelta(
                            days=random.randint(0, 30),
                            hours=random.randint(0, 23),
                            minutes=random.randint(0, 59),
                        ),
                    )
                    db.session.add(action)
                    action_count += 1

            # 生成收藏记录
            for item in fav_items:
                action = UserAction(
                    user_id=user.id,
                    item_id=item.id,
                    action_type='fav',
                    created_at=now - timedelta(
                        days=random.randint(0, 15),
                        hours=random.randint(0, 23),
                    ),
                )
                db.session.add(action)
                action_count += 1

            total_actions += action_count
            print(f"  {user.username}: {len(view_items)}个浏览商品, "
                  f"{len(fav_items)}个收藏, 共{action_count}条行为")

        db.session.commit()
        print(f"\n完成！共生成 {total_actions} 条行为数据")
        print("所有模拟用户密码: pass123")


if __name__ == '__main__':
    seed()
