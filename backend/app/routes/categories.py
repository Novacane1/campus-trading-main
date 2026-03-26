from flask import Blueprint, request, jsonify
from app.models.models import Category, Item, User
from app import db
from flask_jwt_extended import jwt_required, get_jwt_identity

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('/', methods=['GET'])
def get_categories():
    parent_id = request.args.get('parent_id')
    if parent_id:
        categories = Category.query.filter_by(parent_id=parent_id).all()
    else:
        categories = Category.query.filter_by(parent_id=None).all()
    return jsonify({'categories': [category.to_dict() for category in categories]}), 200


@categories_bp.route('/all', methods=['GET'])
@jwt_required(optional=True)
def get_all_categories():
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id) if current_user_id else None
    current_school = current_user.school_name if current_user else None

    categories = Category.query.all()
    cat_map = {}

    for c in categories:
        # 统计在售商品数量（校园隔离：仅统计同校商品）
        if current_school:
            product_count = c.items.join(User, Item.seller_id == User.id).filter(
                Item.status == 'on_sale',
                User.school_name == current_school
            ).count()
        else:
            product_count = c.items.filter_by(status='on_sale').count()

        cat_dict = c.to_dict()
        cat_dict['productCount'] = product_count
        cat_map[str(c.id)] = {**cat_dict, 'children': []}

    tree = []
    for c in categories:
        if c.parent_id:
            parent_key = str(c.parent_id)
            if parent_key in cat_map:
                cat_map[parent_key]['children'].append(cat_map[str(c.id)])
        else:
            tree.append(cat_map[str(c.id)])
    return jsonify(tree), 200


@categories_bp.route('/', methods=['POST'])
def create_category():
    data = request.get_json()
    name = data.get('name')
    parent_id = data.get('parent_id')
    if not name:
        return jsonify({'msg': 'Name is required'}), 400
    category = Category(name=name, parent_id=parent_id)
    db.session.add(category)
    db.session.commit()
    return jsonify(category.to_dict()), 201


@categories_bp.route('/<string:cat_id>', methods=['GET'])
def get_category(cat_id):
    category = Category.query.get_or_404(cat_id)
    return jsonify(category.to_dict()), 200


@categories_bp.route('/<string:cat_id>', methods=['PUT'])
def update_category(cat_id):
    category = Category.query.get_or_404(cat_id)
    data = request.get_json()
    if 'name' in data:
        category.name = data['name']
    if 'parent_id' in data:
        category.parent_id = data['parent_id']
    if 'icon' in data:
        category.icon = data['icon']
    if 'sort_order' in data:
        category.sort_order = data['sort_order']
    db.session.commit()
    return jsonify(category.to_dict()), 200


@categories_bp.route('/<string:cat_id>', methods=['DELETE'])
def delete_category(cat_id):
    category = Category.query.get_or_404(cat_id)
    if category.items.count() > 0:
        return jsonify({'msg': '该分类下有商品，无法删除'}), 400
    db.session.delete(category)
    db.session.commit()
    return jsonify({'msg': '分类已删除'}), 200
