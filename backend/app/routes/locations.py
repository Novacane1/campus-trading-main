from flask import Blueprint, request, jsonify
from app.models.models import Location
from app import db

locations_bp = Blueprint('locations', __name__)


@locations_bp.route('/', methods=['GET'])
def get_locations():
    locations = Location.query.order_by(Location.used_count.desc()).all()
    if not locations:
        # Seed default locations if empty
        defaults = [
            Location(name='图书馆', description='图书馆正门，环境安静，安全可靠', used_count=1256, rating=4.8, distance='50m'),
            Location(name='食堂门口', description='食堂正门，人流量大，交易方便', used_count=2341, rating=4.6, distance='100m'),
            Location(name='教学楼', description='教学楼大厅，环境舒适，适合交易', used_count=987, rating=4.9, distance='80m'),
            Location(name='操场', description='操场看台，视野开阔，安全交易', used_count=765, rating=4.5, distance='150m'),
            Location(name='宿舍楼', description='宿舍楼下，距离近，方便快捷', used_count=543, rating=4.3, distance='30m'),
        ]
        db.session.add_all(defaults)
        db.session.commit()
        locations = defaults
    return jsonify({'locations': [loc.to_dict() for loc in locations]}), 200


@locations_bp.route('/<int:loc_id>', methods=['GET'])
def get_location(loc_id):
    loc = Location.query.get_or_404(loc_id)
    return jsonify(loc.to_dict()), 200


@locations_bp.route('/', methods=['POST'])
def create_location():
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({'msg': '地点名称不能为空'}), 400
    loc = Location(
        name=name,
        description=data.get('description'),
        image=data.get('image'),
        distance=data.get('distance')
    )
    db.session.add(loc)
    db.session.commit()
    return jsonify(loc.to_dict()), 201


@locations_bp.route('/<int:loc_id>', methods=['PUT'])
def update_location(loc_id):
    loc = Location.query.get_or_404(loc_id)
    data = request.get_json()
    if 'name' in data:
        loc.name = data['name']
    if 'description' in data:
        loc.description = data['description']
    if 'image' in data:
        loc.image = data['image']
    if 'distance' in data:
        loc.distance = data['distance']
    db.session.commit()
    return jsonify(loc.to_dict()), 200


@locations_bp.route('/<int:loc_id>', methods=['DELETE'])
def delete_location(loc_id):
    loc = Location.query.get_or_404(loc_id)
    db.session.delete(loc)
    db.session.commit()
    return jsonify({'msg': '地点已删除'}), 200
