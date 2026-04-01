from flask import Blueprint, jsonify, request
from app.models.models import Item, Order, Category
from app import db
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import func

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/overview', methods=['GET'])
def get_overview_stats():
    """General statistics for the dashboard"""
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)

    total_items = Item.query.filter(Item.status != 'deleted').count()
    total_orders = Order.query.count()
    total_revenue = db.session.query(db.func.sum(Order.amount)).scalar() or 0
    previous_total_items = Item.query.filter(
        Item.status != 'deleted',
        db.func.date(Item.created_at) < today
    ).count()
    previous_total_orders = Order.query.filter(
        db.func.date(Order.created_at) < today
    ).count()

    today_items = Item.query.filter(
        db.func.date(Item.created_at) == today
    ).count()
    yesterday_items = Item.query.filter(
        db.func.date(Item.created_at) == yesterday
    ).count()
    today_orders = Order.query.filter(
        db.func.date(Order.created_at) == today
    ).count()
    yesterday_orders = Order.query.filter(
        db.func.date(Order.created_at) == yesterday
    ).count()
    avg_price = db.session.query(db.func.avg(Item.price)).filter(
        Item.status == 'on_sale'
    ).scalar() or 0
    yesterday_avg_price = db.session.query(db.func.avg(Item.price)).filter(
        Item.status == 'on_sale',
        db.func.date(Item.created_at) <= yesterday
    ).scalar() or 0

    return jsonify({
        'total_items': total_items,
        'previous_total_items': previous_total_items,
        'total_orders': total_orders,
        'previous_total_orders': previous_total_orders,
        'total_revenue': float(total_revenue),
        'today_items': today_items,
        'yesterday_items': yesterday_items,
        'today_orders': today_orders,
        'yesterday_orders': yesterday_orders,
        'avg_price': round(float(avg_price), 2),
        'yesterday_avg_price': round(float(yesterday_avg_price), 2)
    }), 200

@stats_bp.route('/price-trends', methods=['GET'])
def get_price_trends():
    """Price trends over time using Pandas"""
    # Get all items from the last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    items = Item.query.filter(Item.created_at >= thirty_days_ago).all()

    if not items:
        return jsonify([]), 200

    df = pd.DataFrame([{
        'date': i.created_at.date(),
        'price': float(i.price),
        'category_id': i.category_id
    } for i in items])

    # Group by date and get mean price
    trends = df.groupby('date')['price'].mean().reset_index()
    trends['date'] = trends['date'].apply(lambda x: x.strftime('%Y-%m-%d'))

    return jsonify(trends.to_dict(orient='records')), 200

@stats_bp.route('/category-distribution', methods=['GET'])
def get_category_distribution():
    """Distribution of items across categories"""
    items = Item.query.all()
    if not items:
        return jsonify([]), 200

    df = pd.DataFrame([{'category_id': i.category_id} for i in items])
    categories = Category.query.all()
    cat_names = {str(c.id): c.name for c in categories}

    df['category_name'] = df['category_id'].apply(lambda x: cat_names.get(str(x), '未知'))
    distribution = df['category_name'].value_counts().reset_index()
    distribution.columns = ['name', 'value']

    return jsonify(distribution.to_dict(orient='records')), 200

@stats_bp.route('/supply-demand', methods=['GET'])
def get_supply_demand():
    """Supply (new items) vs Demand (new orders) over the last 7 days"""
    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    items = Item.query.filter(Item.created_at >= seven_days_ago).all()
    orders = Order.query.filter(Order.created_at >= seven_days_ago).all()

    dates = [(datetime.utcnow() - timedelta(days=i)).date() for i in range(7)]
    dates.reverse()

    supply_map = {}
    demand_map = {}
    for i in items:
        d = i.created_at.date()
        supply_map[d] = supply_map.get(d, 0) + 1
    for o in orders:
        d = o.created_at.date()
        demand_map[d] = demand_map.get(d, 0) + 1

    result = []
    for d in dates:
        result.append({
            'date': d.strftime('%Y-%m-%d'),
            'supply': supply_map.get(d, 0),
            'demand': demand_map.get(d, 0)
        })

    return jsonify(result), 200


@stats_bp.route('/category-price-trends', methods=['GET'])
def get_category_price_trends():
    """按品类统计价格走势"""
    category_id = request.args.get('category_id')
    days = int(request.args.get('days', 30))

    start_date = datetime.utcnow() - timedelta(days=days)

    query = Item.query.filter(Item.created_at >= start_date)
    if category_id:
        query = query.filter(Item.category_id == category_id)

    items = query.all()

    if not items:
        return jsonify([]), 200

    df = pd.DataFrame([{
        'date': i.created_at.date(),
        'price': float(i.price)
    } for i in items])

    trends = df.groupby('date').agg({
        'price': ['mean', 'min', 'max', 'count']
    }).reset_index()

    trends.columns = ['date', 'avg_price', 'min_price', 'max_price', 'count']
    trends['date'] = trends['date'].apply(lambda x: x.strftime('%Y-%m-%d'))

    return jsonify(trends.to_dict(orient='records')), 200


@stats_bp.route('/price-distribution', methods=['GET'])
def get_price_distribution():
    """价格区间分布直方图数据"""
    category_id = request.args.get('category_id')

    query = Item.query.filter(Item.status == 'on_sale')
    if category_id:
        query = query.filter(Item.category_id == category_id)

    items = query.all()

    if not items:
        return jsonify([]), 200

    prices = [float(i.price) for i in items]

    # 定义价格区间
    bins = [0, 50, 100, 200, 500, 1000, 2000, 5000, 10000]
    labels = ['0-50', '50-100', '100-200', '200-500', '500-1000',
              '1000-2000', '2000-5000', '5000+']

    df = pd.DataFrame({'price': prices})
    df['range'] = pd.cut(df['price'], bins=bins + [float('inf')], labels=labels + ['5000+'], right=False)

    distribution = df['range'].value_counts().sort_index().reset_index()
    distribution.columns = ['range', 'count']

    return jsonify(distribution.to_dict(orient='records')), 200


@stats_bp.route('/supply-demand-ratio', methods=['GET'])
def get_supply_demand_ratio():
    """供需比例饼图数据"""
    # 在售商品数（供应）
    on_sale_count = Item.query.filter(Item.status == 'on_sale').count()

    # 最近7天的订单数（需求）
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_orders = Order.query.filter(Order.created_at >= seven_days_ago).count()

    # 已售出商品数
    sold_count = Item.query.filter(Item.status == 'sold').count()

    return jsonify([
        {'name': '在售商品', 'value': on_sale_count},
        {'name': '近7日订单', 'value': recent_orders},
        {'name': '已售商品', 'value': sold_count}
    ]), 200


@stats_bp.route('/category-avg-price', methods=['GET'])
def get_category_avg_price():
    """各品类平均价格对比"""
    items = Item.query.filter(Item.status == 'on_sale').all()

    if not items:
        return jsonify([]), 200

    df = pd.DataFrame([{
        'category_id': str(i.category_id),
        'price': float(i.price)
    } for i in items])

    categories = Category.query.all()
    cat_names = {str(c.id): c.name for c in categories}

    df['category_name'] = df['category_id'].apply(lambda x: cat_names.get(x, '未知'))

    avg_prices = df.groupby('category_name')['price'].mean().reset_index()
    avg_prices.columns = ['category', 'avg_price']
    avg_prices['avg_price'] = avg_prices['avg_price'].round(2)
    avg_prices['name'] = avg_prices['category']

    return jsonify(avg_prices.to_dict(orient='records')), 200
