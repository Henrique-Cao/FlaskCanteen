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
    display_order = request.form.get('display_order', type=int, default=1)

    if not category_name:

        return redirect(url_for('admin.manage_menu'))

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