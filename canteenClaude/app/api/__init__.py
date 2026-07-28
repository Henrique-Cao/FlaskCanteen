from flask import Blueprint
api_bp = Blueprint('api', __name__)

from app.api.menu import menu_api
# Register sub-blueprints
api_bp.register_blueprint(menu_api, url_prefix='/menu')

from app.api.categories import categories_api
api_bp.register_blueprint(categories_api, url_prefix='/categories')