from flask import Flask
from .extensions import db, login_manager, csrf
from .models import User

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"  # فعلاً login route نداریم؛ بعداً می‌سازیم

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Routes
    from .routes import main
    app.register_blueprint(main)

    # Error handlers
    from .routes import not_found
    app.register_error_handler(404, not_found)

    return app
