from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate() 
login_manager = LoginManager()
csrf = CSRFProtect()


login_manager.login_message = "لطفاً برای دسترسی به این صفحه وارد شوید."
login_manager.login_message_category = "info" # برای استایل‌دهی فلش مسیج