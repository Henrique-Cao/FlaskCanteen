from flask import Blueprint, render_template,redirect, url_for, request, flash
from app.services.order_service import get_order_by_numeric_input
from app.models import Category, MenuItem, Order, OrderItem
 
main_bp = Blueprint("main", __name__)
 
 
@main_bp.route("/")
def index():
    return render_template("main/index.html")

@main_bp.route("/menu")
def menu():
    
    categories = Category.query.all()
    menu_items = MenuItem.query.all()
    
    return render_template("menu/menu.html", categories=categories, menu_items=menu_items)

@main_bp.route("/confirmation/<order_number>")
def confirmation(order_number):
    # get the order details from the database using the order_number
    order = Order.query.filter_by(order_number=order_number).first()
    if order is None:
        return render_template("main/index.html", order_number=order_number), 404
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


@main_bp.route("/track_order")
def track_order():
    return render_template("track_order/track_order.html")

@main_bp.route('/track_order', methods=['POST'])
def redirect_tracking():
    if request.method == 'POST':
        # 1. Get submitted digits from <input name="order_number">
        submitted_digits = request.form.get('order_number', '')
        print(submitted_digits)
        # 2. Look up order using our service helper
        order = get_order_by_numeric_input(submitted_digits)
        
        # 3. Redirect if found, otherwise show error
        print(order)
        if order:
            return redirect(url_for('main.confirmation', order_number=order))
        
        flash("No order found with that ID. Please check your receipt and try again.", "danger")

    return render_template('main/confirmation.html', order_number=submitted_digits)