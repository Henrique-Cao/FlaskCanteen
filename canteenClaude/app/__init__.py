"""
app/__init__.py
~~~~~~~~~~~~~~~
Application factory for the Club33 Flask application.
"""
import os
from flask import Flask
from config import config_map
from app.extensions import db, migrate
 

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
 
    # ── Automatically Create Database & Tables ────────────────────────
    # This checks for the database/tables and creates them if missing
    with app.app_context():
        from app.models import MenuItem, Order, OrderItem, Category
        db.create_all()
        

    # ── Blueprints ────────────────────────────────────────────────────
    from app.main.routes   import main_bp
    from app.menu.routes   import menu_bp
    #from app.orders.routes import orders_bp
    from app.admin.routes  import admin_bp
    from app.order_confirmation.routes import order_confirmation_bp

    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(main_bp)
    app.register_blueprint(menu_bp,   url_prefix="/menu")
    #app.register_blueprint(orders_bp, url_prefix="/orders")
    app.register_blueprint(admin_bp,  url_prefix="/admin")
    app.register_blueprint(order_confirmation_bp, url_prefix="/order_confirmation")
    
    # ── Shell context ─────────────────────────────────────────────────
    @app.shell_context_processor
    def make_shell_context():
        from app.models import MenuItem, Order, OrderItem
        return {"db": db, "MenuItem": MenuItem, "Order": Order, "OrderItem": OrderItem}
 
    return app