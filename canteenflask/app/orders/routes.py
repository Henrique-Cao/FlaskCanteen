from flask import Blueprint, render_template
from app.models import Category, MenuItem
order_bp = Blueprint("order", __name__)
 
 
@order_bp.route("/")
def index():

       
    return render_template("orders/orders.html")
 