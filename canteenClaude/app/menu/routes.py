from flask import Blueprint, render_template
 
menu_bp = Blueprint("menu", __name__)
 
 
@menu_bp.route("/")
def index():
    """Menu page."""
    return render_template("menu/menu.html")
 