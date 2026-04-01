import os
from datetime import timedelta
from textwrap import wrap
from dotenv import load_dotenv

load_dotenv()


def normalize_pem_key(value, key_kind='public'):
    value = (value or '').strip()
    if not value:
        return ''

    # Support values stored with escaped newlines or already-complete PEM blocks.
    value = value.replace('\\n', '\n')
    if '-----BEGIN' in value:
        return value

    chunks = '\n'.join(wrap(value, 64))
    if key_kind == 'private':
        return f'-----BEGIN RSA PRIVATE KEY-----\n{chunks}\n-----END RSA PRIVATE KEY-----'
    return f'-----BEGIN PUBLIC KEY-----\n{chunks}\n-----END PUBLIC KEY-----'

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-me-secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'change-me-jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # PostgreSQL Configuration
    DB_USER = os.environ.get('DB_USER') or 'campus'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'change-me-db-password'
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_PORT = os.environ.get('DB_PORT') or '5432'
    DB_NAME = os.environ.get('DB_NAME') or 'campus_trading'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    
    # Redis Configuration
    REDIS_HOST = os.environ.get('REDIS_HOST') or 'localhost'
    REDIS_PORT = os.environ.get('REDIS_PORT') or 6379
    REDIS_DB = os.environ.get('REDIS_DB') or 0
    
    # Upload Configuration
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # PicUI 图床配置
    PICUI_API_TOKEN = os.environ.get('PICUI_API_TOKEN') or ''

    # Alipay Sandbox / Production Configuration
    ALIPAY_APP_ID = os.environ.get('ALIPAY_APP_ID') or ''
    ALIPAY_GATEWAY = os.environ.get('ALIPAY_GATEWAY') or 'https://openapi-sandbox.dl.alipaydev.com/gateway.do'
    ALIPAY_APP_PUBLIC_KEY = normalize_pem_key(os.environ.get('ALIPAY_APP_PUBLIC_KEY') or '', 'public')
    ALIPAY_APP_PRIVATE_KEY = normalize_pem_key(os.environ.get('ALIPAY_APP_PRIVATE_KEY') or '', 'private')
    ALIPAY_PUBLIC_KEY = normalize_pem_key(os.environ.get('ALIPAY_PUBLIC_KEY') or '', 'public')
    ALIPAY_NOTIFY_URL = os.environ.get('ALIPAY_NOTIFY_URL') or ''
    ALIPAY_RETURN_URL = os.environ.get('ALIPAY_RETURN_URL') or ''
    ALIPAY_DEBUG = str(os.environ.get('ALIPAY_DEBUG') or 'true').lower() in ('1', 'true', 'yes', 'on')
