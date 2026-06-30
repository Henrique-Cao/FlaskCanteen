from flask import Blueprint, render_template,request, jsonify, redirect, url_for
from app.models import MenuItem
admin_bp = Blueprint("admin", __name__)
from collections import defaultdict
 
@admin_bp.route("/")
def index():
    """Menu page."""
    return render_template("admin/dashboard.html")
@admin_bp.route('/admin/manage-menu', methods=['GET'])
def manage_menu():
    search_query = request.args.get('search', '').strip()
    
    # 1. Select the core lookup dataset from SQLite database
    query = MenuItem.query
    if search_query:
        query = query.filter(MenuItem.name.ilike(f"%{search_query}%"))
    
    all_items = query.order_by(MenuItem.name.asc()).all()
    
    # 2. Re-map data structurally array bucket categories on the fly
    items_by_category = defaultdict(list)
    for item in all_items:
        items_by_category[item.category].append(item)
        
    return render_template('admin/manage_menu.html', 
                           items_by_category=items_by_category, 
                           search_query=search_query)