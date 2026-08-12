from flask import Blueprint, render_template,request, jsonify, redirect, url_for
from app.models import MenuItem,Category,Order
admin_bp = Blueprint("admin", __name__)
from collections import defaultdict
 
@admin_bp.route("/")
def index():
    
    
    return render_template("admin/analytics.html")
@admin_bp.route('/manage-menu', methods=['GET'])
def manage_menu():
    search_query = request.args.get('search', '').strip()
    
    # 1. Select the core lookup dataset from SQLite database
    query = MenuItem.query
    if search_query:
        query = query.filter(MenuItem.name.ilike(f"%{search_query}%"))
    
    all_items = query.order_by(MenuItem.name.asc()).all()
    
  
    #2. Create a dictionary to hold items by category in the order of the categories
    items_by_category = defaultdict(list)
    categories = Category.query.order_by(Category.display_order.asc()).all()
    for category in categories:
        items_by_category[category.name] = [item for item in all_items if item.category_id == category.id]
    
    category_query = Category.query.order_by(Category.display_order.asc()).all()
    for item in all_items:
            if item.category is None:
                items_by_category["Uncategorized"].append(item)
    return render_template('admin/manage_menu.html', 
                           items_by_category=items_by_category, 
                           search_query=search_query,
                           categories=category_query)
@admin_bp.route('/orders')
def order_management():
    """Render the order management page."""
    orders = Order.query.order_by(Order.created_at.desc()).all()

    return render_template('admin/orders.html', orders=orders)


