"""
app/__init__.py
~~~~~~~~~~~~~~~
Application factory for the Club33 Flask application.
"""
import os
from flask import Flask
from config import config_map
from app.extensions import db, migrate
 
from flask_login import LoginManager, UserMixin
from app.models import User

login_manager = LoginManager()


def create_app(config_name: str | None = None) -> Flask:
    """Create and configure the Flask application instance."""  
    config_name = config_name or os.environ.get("FLASK_ENV", "default")
 
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
        
    )
    app.secret_key = os.environ.get("SECRET_KEY", "default_secret_key")
    app.config.from_object(config_map.get(config_name, config_map["default"]))
 
    # ── Extensions ────────────────────────────────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = "main_bp.login"  # Redirect to login page if not authenticated

    # 2. Tell Flask-Login how to look up users by session ID
    @login_manager.user_loader
    def load_user(user_id):
        try:

            return db.session.get(User, int(user_id))
        except (ValueError, TypeError):
            return None

    
    # ── Automatically Create Database & Tables ────────────────────────
    # This checks for the database/tables and creates them if missing
    with app.app_context():
        from app.models import MenuItem, Order, OrderItem, Category,User
        db.create_all()
        

    # ── Blueprints ────────────────────────────────────────────────────
    from app.main.routes   import main_bp
    from app.admin.routes  import admin_bp
    from app.api.authentication import auth_api


    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp,  url_prefix="/admin")
    app.register_blueprint(auth_api, url_prefix='/api/auth')

    
    # ── Shell context ─────────────────────────────────────────────────
    @app.shell_context_processor
    def make_shell_context():
        from app.models import MenuItem, Order, OrderItem
        return {"db": db, "MenuItem": MenuItem, "Order": Order, "OrderItem": OrderItem}
 
    return app