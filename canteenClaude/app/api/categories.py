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
    # Extract the form fields using the 'name' attribute from your HTML input elements
    category_name = request.form.get('name')

    if not category_name:

        return redirect(url_for('admin.manage_menu'))

    display_order = db.session.query(Category).count() + 1  # Set display order to the next available position
    print(f"Adding new category: {category_name} with display order: {display_order}")  # Debugging line
    new_category = Category(name=category_name, display_order=display_order)
    db.session.add(new_category)
    db.session.commit()


    return redirect(url_for('admin.manage_menu'))

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
    new_name = data.get('name')
    
    if not new_name:
        return jsonify({'success': False, 'message': 'Category name is required.'}), 400

    category.name = new_name
    db.session.commit()
    return redirect(url_for('admin.manage_menu'))