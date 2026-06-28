# config.py (نسخه ساده - بدون نیاز به .env)
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '2400116326'
    
    # دیتابیس
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    } if DATABASE_URL else {}
    
    # تنظیمات آپلود
    UPLOAD_FOLDER = os.path.join(basedir, 'app/static/uploads/projects')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    # ========== تنظیمات ملی پیامک ==========
    MELIPAYAMAK_USERNAME = os.environ.get('MELIPAYAMAK_USERNAME') or 'your_username'
    MELIPAYAMAK_PASSWORD = os.environ.get('MELIPAYAMAK_PASSWORD') or 'your_password'
    MELIPAYAMAK_PATTERN_CODE = os.environ.get('MELIPAYAMAK_PATTERN_CODE') or '12345'  # کد الگوی ساخته‌شده در پنل
    MELIPAYAMAK_FROM = os.environ.get('MELIPAYAMAK_FROM') or '5000...'  # شماره فرستنده (اختیاری)
    
    # تنظیمات GIS
    DEFAULT_SRID = int(os.environ.get('DEFAULT_SRID', 4326))