from flask import Blueprint, jsonify, request, redirect, url_for,flash
from app.extensions import db
from app.models import Category, MenuItem

categories_api = Blueprint('categories_api', __name__)

@categories_api.route('/', methods=['GET'])
def get_all_categories():
    categories = Category.query.order_by(Category.display_order).all()
    serialized_categories = [
        {
            "id": category.id,
            "name": category.name,
            "display_order": category.display_order
        } for category in categories
    ]
    return jsonify(serialized_categories), 200

@categories_api.route('/add', methods=['POST'])
def add_category():
    data = request.get_json()
    category_name = data.get('name')
    print(f"Received request to add category with name: {category_name}")  # Debugging line
    if not category_name:
        return jsonify({'success': False, 'message': 'Category name is required.'}), 400

    # Determine the next display order
    max_order = db.session.query(db.func.max(Category.display_order)).scalar() or 0
    new_category = Category(name=category_name, display_order=max_order + 1)
    
    db.session.add(new_category)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Category "{new_category.name}" added successfully!',
        'category': {
            'id': new_category.id,
            'name': new_category.name,
            'display_order': new_category.display_order
        }
    }), 201


    

@categories_api.route('/delete/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    print(f"Attempting to delete category with ID: {category_id}")  # Debugging line
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash(f'Category "{category.name}" deleted successfully!', 'success')
    return jsonify({
        'success': True,
        'message': f'Category "{category.name}" deleted successfully!'
    }), 200

@categories_api.route('/reorder', methods=['POST'])
def reorder_categories():

    data = request.get_json()
    new_order = data.get('ordered_ids', [])

    for index, category_id in enumerate(new_order):
        category = Category.query.get(category_id)
        if category:
            category.display_order = index + 1  # Update display order based on the new position
            db.session.add(category)

    db.session.commit()
    return jsonify({'success': True, 'message': 'Categories reordered successfully!'}), 200
@categories_api.route('/update/<int:category_id>', methods=['POST'])
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    data = request.get_json()
    new_name = data.get('name', '').strip()

    
    if not new_name:
        return jsonify({'success': False, 'message': 'Category name is required.'}), 400

    category.name = new_name
    db.session.commit()


    return jsonify({
        'success': True,
        'message': f'Category "{category.name}" updated successfully!',
        'category': {
            'id': category.id,
            'name': category.name,
            'display_order': category.display_order
        } 
    }), 200