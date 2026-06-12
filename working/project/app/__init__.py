from flask import Flask
from .extensions import db, login_manager, csrf, migrate
from config import Config
from .models import User # اینجا هم برای اطمینان
from .admin_routes import admin_bp  # ← ایمپورت در ابتدا

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['SECRET_KEY'] = '2400116326'
    
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db) # اتصال migrate به app و db
    
    login_manager.login_view = 'main.login'
    login_manager.login_message = "لطفا برای دسترسی به این صفحه وارد شوید."
    login_manager.login_message_category = "warning"
    # این خط بسیار مهم است: مدل‌ها را لود می‌کند تا migrate آن‌ها را ببیند
    from . import models 

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User # اینجا هم برای اطمینان
        return User.query.get(int(user_id))
    
    # Routes
    from .routes import main
    app.register_blueprint(main)

    # Error handlers
    from .routes import not_found
    app.register_error_handler(404, not_found)

    # روش دوم: ایمپورت درون تابع (اگر روش اول جواب نداد)
    try:
        from .admin_routes import admin_bp
        app.register_blueprint(admin_bp)
    except ImportError:
        print("Admin routes not found")

     # ثبت Blueprint مدیریت
    
    return app
