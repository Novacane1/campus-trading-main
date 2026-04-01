import os
import secrets

from app import create_app, db
from app.models.models import Category, User, Location, StudentVerification

app = create_app()


def _resolve_default_admin_password():
    configured_password = (os.environ.get('DEFAULT_ADMIN_PASSWORD') or '').strip()
    if configured_password:
        return configured_password, False
    return secrets.token_urlsafe(12), True

@app.cli.command("init-db")
def init_db():
    """Initialize the database with default data."""
    db.create_all()

    # Default categories (Chinese names matching frontend)
    categories = [
        ('数码产品', None), ('图书教材', None), ('运动装备', None),
        ('生活用品', None), ('服装鞋包', None), ('其他物品', None)
    ]
    for cat_name, parent in categories:
        if not Category.query.filter_by(name=cat_name).first():
            db.session.add(Category(name=cat_name, parent_id=parent))

    # Default locations
    locs = [
        ('图书馆', '图书馆正门，环境安静，安全可靠', 1256, 4.8, '50m'),
        ('食堂门口', '食堂正门，人流量大，交易方便', 2341, 4.6, '100m'),
        ('教学楼', '教学楼大厅，环境舒适，适合交易', 987, 4.9, '80m'),
        ('操场', '操场看台，视野开阔，安全交易', 765, 4.5, '150m'),
        ('宿舍楼', '宿舍楼下，距离近，方便快捷', 543, 4.3, '30m'),
    ]
    for name, desc, count, rating, dist in locs:
        if not Location.query.filter_by(name=name).first():
            db.session.add(Location(name=name, description=desc,
                                    used_count=count, rating=rating, distance=dist))

    # Default admin user (student_id='admin' is used for admin auth)
    if not User.query.filter_by(username='admin').first():
        admin_password, generated_password = _resolve_default_admin_password()
        admin = User(
            username='admin',
            school_name='系统管理员',
            student_id='admin',
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        print(f"Admin user created: username=admin, password={admin_password}")
        if generated_password:
            print("DEFAULT_ADMIN_PASSWORD 未设置，已为管理员生成随机密码。")

    # 虚拟学信网数据（模拟学生身份验证库）
    students = [
        ('北京大学', '2021001001', '张三'),
        ('北京大学', '2021001002', '李四'),
        ('北京大学', '2022001001', '王五'),
        ('清华大学', '2021002001', '赵六'),
        ('清华大学', '2022002001', '钱七'),
        ('清华大学', '2022002002', '孙八'),
        ('复旦大学', '2021003001', '周九'),
        ('复旦大学', '2022003001', '吴十'),
        ('浙江大学', '2021004001', '郑十一'),
        ('浙江大学', '2022004001', '冯十二'),
        ('南京大学', '2021005001', '陈十三'),
        ('南京大学', '2022005001', '褚十四'),
        ('武汉大学', '2021006001', '卫十五'),
        ('武汉大学', '2022006001', '蒋十六'),
        ('中山大学', '2021007001', '沈十七'),
        ('中山大学', '2022007001', '韩十八'),
        ('四川大学', '2021008001', '杨十九'),
        ('四川大学', '2022008001', '朱二十'),
        ('华中科技大学', '2021009001', '秦廿一'),
        ('华中科技大学', '2022009001', '许廿二'),
    ]
    for school, sid, name in students:
        if not StudentVerification.query.filter_by(school_name=school, student_id=sid).first():
            db.session.add(StudentVerification(school_name=school, student_id=sid, real_name=name))
    print("Student verification data initialized!")

    db.session.commit()
    print("Database initialized!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5001)
