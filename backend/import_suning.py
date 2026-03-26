"""
导入苏宁易购爬取的商品数据到 items 表。
用法：cd backend && python import_suning.py
"""
import sys, os, json, random, re
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models.models import Item

# ==================== 配置 ====================

# 分类名 → UUID（与数据库 categories 表对应）
CATEGORY_NAME_TO_ID = {
    '数码产品': '04990b17-7c49-42f2-91f4-9226abd879f4',
    '图书教材': '8558e9f8-2212-49f3-9c71-9a40c859779a',
    '运动装备': '61c35377-943d-4c5c-8afc-68b19ae6126b',
    '生活用品': 'a0d67dc4-aa41-4c2c-9060-eee5f3a7e432',
    '服装鞋包': 'd9924fff-209c-4bc2-8e31-74deb97ca38a',
    '其他物品': '9cbd4f89-c236-4f58-ac43-1e143bc495e4',
}

SELLER_IDS = [1, 2, 3, 4, 5]
LOCATIONS = ['图书馆', '食堂门口', '教学楼', '操场', '宿舍楼', '体育馆', '校门口', '快递站']
CONDITIONS = ['全新', '几乎全新', '稍有瑕疵', '7成新以下']

TIME_SLOTS = [
    '周一 08:00-12:00', '周一 14:00-18:00',
    '周二 08:00-12:00', '周二 14:00-18:00',
    '周三 08:00-12:00', '周三 14:00-18:00',
    '周四 08:00-12:00', '周四 14:00-18:00',
    '周五 08:00-12:00', '周五 14:00-18:00',
    '周六 10:00-16:00', '周日 10:00-16:00',
]

PREFERRED_LOCS = ['图书馆', '食堂', '宿舍楼下', '教学楼大厅', '快递站', '校门口']

# ==================== 工具函数 ====================

def parse_price(price_str):
    """解析价格字符串，如 '¥2,719.15' → 2719.15"""
    cleaned = re.sub(r'[¥￥,\s]', '', price_str)
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def random_time_slots():
    """随机生成 1~3 个可交易时间窗"""
    return random.sample(TIME_SLOTS, k=random.randint(1, 3))


def random_preferred_locations():
    """随机生成 1~2 个偏好地点"""
    return random.sample(PREFERRED_LOCS, k=random.randint(1, 2))


# ==================== 主逻辑 ====================

def import_products():
    json_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'products.json')
    json_path = os.path.abspath(json_path)

    if not os.path.exists(json_path):
        print(f"文件不存在: {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        products = json.load(f)

    print(f"读取到 {len(products)} 条商品数据")

    app = create_app()
    with app.app_context():
        now = datetime.now()
        count = 0
        skipped = 0

        for p in products:
            # 解析分类
            category_name = p.get('category', '')
            category_id = CATEGORY_NAME_TO_ID.get(category_name)
            if not category_id:
                print(f"  跳过（未知分类 '{category_name}'）: {p.get('name', '')[:30]}")
                skipped += 1
                continue

            # 解析价格
            price = parse_price(p.get('price', '0'))
            if price <= 0:
                print(f"  跳过（价格无效）: {p.get('name', '')[:30]}")
                skipped += 1
                continue

            # 校园二手价：苏宁原价打折，模拟二手售价
            campus_price = round(price * random.uniform(0.3, 0.75), 2)

            # 商品名截断到 128 字符
            name = (p.get('name', '') or '未知商品')[:128]
            description = p.get('description', '') or ''

            # 图片：优先使用网络图片 URL
            image_url = p.get('image_url', '')
            images = [image_url] if image_url else []

            item = Item(
                name=name,
                description=description,
                price=campus_price,
                images=images,
                category_id=category_id,
                seller_id=random.choice(SELLER_IDS),
                location=random.choice(LOCATIONS),
                condition=random.choice(CONDITIONS),
                status='on_sale',
                created_at=now - timedelta(
                    days=random.randint(0, 90),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59),
                ),
                available_time_slots=random_time_slots(),
                preferred_locations=random_preferred_locations(),
            )
            db.session.add(item)
            count += 1

            # 每 200 条提交一次，避免内存过大
            if count % 200 == 0:
                db.session.commit()
                print(f"  已导入 {count} 条...")

        db.session.commit()
        print(f"\n导入完成！共插入 {count} 条商品，跳过 {skipped} 条")


if __name__ == '__main__':
    import_products()
