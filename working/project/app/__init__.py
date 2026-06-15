# app/__init__.py
from flask import Flask
from .extensions import db, login_manager, csrf
from config import Config
import jdatetime  # نصب: pip install jdatetime

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    
    login_manager.login_view = "main.login"
    login_manager.login_message = "لطفا برای دسترسی به این صفحه وارد شوید."
    
    from . import models
    
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))
    
    # ========== فیلتر تاریخ شمسی ==========
    @app.template_filter('to_jalali')
    def to_jalali_filter(date):
        """تبدیل تاریخ میلادی به شمسی"""
        if date is None:
            return '-'
        try:
            jalali_date = jdatetime.datetime.fromgregorian(datetime=date)
            return jalali_date.strftime('%Y/%m/%d')
        except:
            return str(date)
    
    # ثبت Blueprintها
    from .routes import main
    app.register_blueprint(main)
    
    try:
        from .admin_routes import admin_bp
        app.register_blueprint(admin_bp)
    except ImportError:
        print("⚠️ Admin routes not found")
    
    from .routes import not_found
    app.register_error_handler(404, not_found)
    
    return app