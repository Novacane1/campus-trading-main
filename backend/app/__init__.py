from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import redis
from werkzeug.exceptions import HTTPException
from config.config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
redis_client = None

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='../static')
    app.url_map.strict_slashes = False
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    jwt.init_app(app)

    # Initialize Redis
    global redis_client
    try:
        redis_client = redis.StrictRedis(
            host=app.config['REDIS_HOST'],
            port=app.config['REDIS_PORT'],
            db=app.config['REDIS_DB'],
            decode_responses=True
        )
        redis_client.ping()
        print("Redis connected successfully")
    except Exception as e:
        print(f"Redis connection failed: {e}. Running without Redis.")
        redis_client = None

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.items import items_bp
    from app.routes.categories import categories_bp
    from app.routes.orders import orders_bp
    from app.routes.stats import stats_bp
    from app.routes.locations import locations_bp
    from app.routes.chat import chat_bp
    from app.routes.admin import admin_bp
    from app.routes.cart import cart_bp
    from app.routes.applications import applications_bp
    from app.routes.verification import verification_bp
    from app.routes.recommendations import recommendations_bp
    from app.routes.risk import risk_bp
    from app.routes.time_location import time_location_bp
    from app.routes.review import review_bp
    from app.routes.announcements import announcement_bp
    from app.routes.banners import banner_bp
    from app.routes.payments import payments_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(items_bp, url_prefix='/api/items')
    app.register_blueprint(categories_bp, url_prefix='/api/categories')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(stats_bp, url_prefix='/api/stats')
    app.register_blueprint(locations_bp, url_prefix='/api/locations')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    app.register_blueprint(applications_bp, url_prefix='/api/applications')
    app.register_blueprint(verification_bp, url_prefix='/api/verification')
    app.register_blueprint(recommendations_bp, url_prefix='/api/recommendations')
    app.register_blueprint(risk_bp, url_prefix='/api/risk')
    app.register_blueprint(time_location_bp, url_prefix='/api/time-location')
    app.register_blueprint(review_bp)
    app.register_blueprint(announcement_bp, url_prefix='/api/announcements')
    app.register_blueprint(banner_bp, url_prefix='/api/banners')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')

    # 启动订单超时定时任务
    from app.services.scheduler import init_scheduler
    init_scheduler(app)

    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}, 200

    @app.route('/')
    def index():
        return {
            'message': 'Welcome to Campus Trading System API',
            'status': 'running',
            'endpoints': {
                'health': '/health',
                'auth': '/api/auth',
                'items': '/api/items',
                'categories': '/api/categories',
                'orders': '/api/orders',
                'stats': '/api/stats'
            }
        }, 200

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Return JSON errors for all API routes."""
        if request.path.startswith('/api/'):
            return jsonify({
                'error': error.name,
                'message': error.description,
                'status_code': error.code
            }), error.code
        return error

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error):
        """Ensure API unexpected failures are returned as JSON."""
        app.logger.exception("Unhandled exception: %s", error)
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Internal Server Error',
                'message': '服务器内部错误',
                'status_code': 500
            }), 500
        return jsonify({
            'error': 'Internal Server Error',
            'message': '服务器内部错误',
            'status_code': 500
        }), 500

    return app
