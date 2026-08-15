from flask import Blueprint, render_template,request, jsonify, redirect, url_for
from app.models import MenuItem,Category,Order
admin_bp = Blueprint("admin", __name__)
from collections import defaultdict
from app.services.order_service import get_filtered_orders_query
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
    Calculates a sliding range of page numbers.
    
    Example: 
    If you are on page 4 out of 10 pages, this returns range(2, 7),
    which renders page buttons: [2, 3, 4, 5, 6].
    """
    # 1. If total pages are fewer than or equal to window size, show all pages
    if total_pages <= window_size:
        return range(1, total_pages + 1)

    # 2. Calculate how many pages to show before and after the current page
    half_window = window_size // 2
    start_page = current_page - half_window
    end_page = current_page + half_window

    # 3. Prevent start page from dropping below 1
    if start_page < 1:
        start_page = 1
        end_page = window_size

    # 4. Prevent end page from exceeding total available pages
    if end_page > total_pages:
        end_page = total_pages
        start_page = total_pages - window_size + 1

    return range(start_page, end_page + 1)

    return range(start_page, end_page + 1)
# History Page routing
@admin_bp.route('/history')
def order_history():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of orders per page

    query = get_filtered_orders_query(request.args)
    # Fetch paginated orders from database
    orders = query.filter_by(status='collected') \
                        .order_by(Order.created_at.desc()) \
                        .paginate(page=page, per_page=per_page, error_out=False)

    # Calculate fixed 5-page window range
    page_range = calculate_pagination_window(
        current_page=orders.page,
        total_pages=orders.pages,
        window_size=5
    )

    # 5. Count active filters to display a badge on the filter button
    statuses = request.args.getlist('status')
    date_preset = request.args.get('date_preset', '')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    active_filters_count = len(statuses) + (1 if date_preset else 0) + (1 if min_price or max_price else 0)
    

    return render_template('admin/history.html', orders=orders, page_range=page_range,active_filters_count=active_filters_count)

