from flask import Blueprint, session, request, jsonify

# 1. Properly instantiate the Blueprint
cart_api = Blueprint('cart_api', __name__)

# 2. Update the route to match the JS endpoint '/add_to_cart'
@cart_api.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    print("Received request to add item to cart")
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON body.'}), 400

    item_id = data.get('item_id')
    quantity = 1 
    print(f"Adding item to cart: {item_id}, Quantity: {quantity}")

    if not item_id:
        return jsonify({'success': False, 'message': 'Item ID is required.'}), 400

    # Initialize cart in session if it doesn't exist
    if 'cart' not in session:
        session['cart'] = {}

    # Add or update item
    if item_id in session['cart']:
        session['cart'][item_id] += quantity
    else:
        session['cart'][item_id] = quantity

    session.modified = True

    return jsonify({
        'success': True,
        'message': f'Item {item_id} added to cart.',
        'cart': session['cart']
    }), 200