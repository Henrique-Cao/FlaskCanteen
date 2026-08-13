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


def calculate_pagination_window(current_page: int, total_pages: int, window_size: int = 5) -> range:
    """
    Calculates a sliding range of page numbers centered around the current page.
    Guarantees exactly `window_size` page numbers when total_pages >= window_size.
    """
    if total_pages <= window_size:
        return range(1, total_pages + 1)

    half_window = window_size // 2
    start_page = current_page - half_window
    end_page = current_page + half_window

    # Left boundary check
    if start_page < 1:
        start_page = 1
        end_page = window_size

    # Right boundary check
    if end_page > total_pages:
        end_page = total_pages
        start_page = total_pages - window_size + 1

    return range(start_page, end_page + 1)
# History Page routing
@admin_bp.route('/history')
def order_history():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of orders per page

    # Fetch paginated orders from database
    orders = Order.query.filter_by(status='collected') \
                        .order_by(Order.created_at.desc()) \
                        .paginate(page=page, per_page=per_page, error_out=False)
    order_items = {order.id: order.items for order in orders.items}
    # Calculate fixed 5-page window range
    page_range = calculate_pagination_window(
        current_page=orders.page, 
        total_pages=orders.pages, 
        window_size=5
    )
    return render_template('admin/history.html', orders=orders, page_range=page_range, order_items=order_items)

