# config.py (نسخه ساده - بدون نیاز به .env)
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = '2400116326'
    
    # اتصال مستقیم به PostgreSQL
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:2400116326@localhost:5432/gis_db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
    
    UPLOAD_FOLDER = os.path.join(basedir, 'app/static/uploads/content')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'app/static/uploads/projects')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB