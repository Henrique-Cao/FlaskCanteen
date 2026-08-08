from flask import Blueprint, render_template
from app.models import Category, MenuItem
order_confirmation_bp = Blueprint("order_confirmation", __name__)
 
 
@order_confirmation_bp.route("/")
def index():

       
    return render_template("order_confirmation/order_confirmation.html")
 