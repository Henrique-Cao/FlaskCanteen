from flask import Blueprint, render_template
from app.models import Category, MenuItem, Order, OrderItem
order_confirmation_bp = Blueprint("order_confirmation", __name__)
 
 
@order_confirmation_bp.route("/<order_number>")
def index(order_number):
    # get the order details from the database using the order_number
    order = Order.query.filter_by(order_number=order_number).first()
    order_items = OrderItem.query.filter_by(order_id=order.id).all() if order else []
    items_with_details = []
    for item in order_items:
        menu_item = MenuItem.query.get(item.menu_item_id)
        if menu_item:
            items_with_details.append({
                "name": menu_item.name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total_price": item.quantity * item.unit_price
            })
        
    return render_template("order_confirmation/order_confirmation.html", order=order, order_items=order_items, order_number=order_number, items_with_details=items_with_details )




 