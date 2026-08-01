from flask import Blueprint, render_template
from app.models import Category, MenuItem
menu_bp = Blueprint("menu", __name__)
 
 
@menu_bp.route("/")
def index():
    """Menu page."""

    categories = Category.query.all()
    menu_items = MenuItem.query.all()
    
    return render_template("menu/menu.html", categories=categories, menu_items=menu_items)
 