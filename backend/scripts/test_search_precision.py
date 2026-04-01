import os
import sys
from decimal import Decimal
from uuid import uuid4

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import create_app, db
from app.models.models import Category, Item, User


PREFIX = "[search-regression]"


def report(ok, title, detail=""):
    status = "PASS" if ok else "FAIL"
    suffix = f" - {detail}" if detail else ""
    print(f"  [{status}] {title}{suffix}")
    return ok


def ensure_test_user():
    user = User.query.filter_by(username="search_regression_user").first()
    if user:
        return user

    user = User(
        username="search_regression_user",
        school_name="搜索回归学校",
        student_id=f"search-{uuid4().hex[:12]}",
        can_publish=True
    )
    user.set_password("search-regression-pass")
    db.session.add(user)
    db.session.commit()
    return user


def cleanup_temp_items():
    Item.query.filter(Item.name.like(f"{PREFIX}%")).delete(synchronize_session=False)
    db.session.commit()


def main():
    app = create_app()
    passed = 0
    failed = 0

    print("=" * 56)
    print("  搜索精度回归测试")
    print("=" * 56)

    with app.app_context():
        cleanup_temp_items()

        category = Category.query.first()
        user = ensure_test_user()
        if not category:
            print("  [FAIL] 未找到分类数据，无法执行搜索测试")
            return 1

        items = [
            Item(
                seller_id=user.id,
                category_id=category.id,
                name=f"{PREFIX} 夏季直筒裤子",
                description="测试用裤子商品",
                price=Decimal("39.90"),
                condition="9成新",
                location="图书馆",
                status="on_sale",
                quantity=1
            ),
            Item(
                seller_id=user.id,
                category_id=category.id,
                name=f"{PREFIX} 复古牛仔裤",
                description="测试用牛仔裤商品",
                price=Decimal("59.90"),
                condition="9成新",
                location="图书馆",
                status="on_sale",
                quantity=1
            ),
            Item(
                seller_id=user.id,
                category_id=category.id,
                name=f"{PREFIX} 宽松卫衣外套",
                description="测试用上衣商品",
                price=Decimal("49.90"),
                condition="9成新",
                location="图书馆",
                status="on_sale",
                quantity=1
            ),
        ]
        db.session.add_all(items)
        db.session.commit()

        client = app.test_client()

        try:
            pants_resp = client.get("/api/items", query_string={"q": "裤子", "limit": 20})
            pants_names = [item["name"] for item in pants_resp.get_json().get("products", [])]
            ok = f"{PREFIX} 夏季直筒裤子" in pants_names and f"{PREFIX} 复古牛仔裤" in pants_names
            if report(ok, "搜索“裤子”命中裤装结果", str(pants_names[:6])):
                passed += 1
            else:
                failed += 1

            ok = f"{PREFIX} 宽松卫衣外套" not in pants_names
            if report(ok, "搜索“裤子”不再误召回上衣", str(pants_names[:6])):
                passed += 1
            else:
                failed += 1

            jeans_resp = client.get("/api/items", query_string={"q": "牛仔裤", "limit": 20})
            jeans_names = [item["name"] for item in jeans_resp.get_json().get("products", [])]
            ok = f"{PREFIX} 复古牛仔裤" in jeans_names
            if report(ok, "搜索“牛仔裤”保留精准匹配", str(jeans_names[:6])):
                passed += 1
            else:
                failed += 1

            ok = f"{PREFIX} 宽松卫衣外套" not in jeans_names
            if report(ok, "搜索“牛仔裤”不扩散到整类衣服", str(jeans_names[:6])):
                passed += 1
            else:
                failed += 1

            apparel_resp = client.get("/api/items", query_string={"q": "衣服", "limit": 200})
            apparel_names = [item["name"] for item in apparel_resp.get_json().get("products", [])]
            ok = (
                f"{PREFIX} 宽松卫衣外套" in apparel_names and
                f"{PREFIX} 夏季直筒裤子" in apparel_names
            )
            if report(ok, "搜索“衣服”仍能命中广义服装", str(apparel_names[:10])):
                passed += 1
            else:
                failed += 1
        finally:
            cleanup_temp_items()

    print("=" * 56)
    print(f"  测试汇总: PASS={passed} FAIL={failed}")
    print("=" * 56)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
