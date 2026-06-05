import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
            SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key' # یک کلید مخفی برای امنیت سشن‌ها
            SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                'sqlite:///' + os.path.join(basedir, 'database.db')
            SQLALCHEMY_TRACK_MODIFICATIONS = False # برای جلوگیری از هشدارهای اضافه
             # تنظیمات آپلود فایل
            UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'app/static/uploads/projects')
            ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
            MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size