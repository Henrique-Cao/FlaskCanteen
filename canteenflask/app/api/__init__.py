from flask import Blueprint
api_bp = Blueprint('api', __name__)

from app.api.menu import menu_api
# Register sub-blueprints
api_bp.register_blueprint(menu_api, url_prefix='/menu')

from app.api.categories import categories_api
api_bp.register_blueprint(categories_api, url_prefix='/categories')

from app.api.cart import cart_api
api_bp.register_blueprint(cart_api, url_prefix='/cart')

from app.api.order import order_api
api_bp.register_blueprint(order_api, url_prefix='/order')

from app.api.analytics import analytics_api
api_bp.register_blueprint(analytics_api, url_prefix='/analytics')
