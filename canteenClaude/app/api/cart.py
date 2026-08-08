from flask import Blueprint, session, request, jsonify

try:
    from app.models import MenuItem
except Exception:
    # Keep this API module import-safe when the model layer is not available.
    MenuItem = None

# 1. Properly instantiate the Blueprint
cart_api = Blueprint('cart_api', __name__)

# 2. Update the route to match the JS endpoint '/add_to_cart'
@cart_api.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON body.'}), 400

    item_id = data.get('item_id')
    quantity = 1 
    
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
    print(f"Current cart contents: {session['cart']}")  # Debugging statement
    return jsonify({
        'success': True,
        'message': f'Item {item_id} added to cart.',
        'cart': session['cart']
    }), 200
@cart_api.route('/clear', methods=['POST'])
def clear_cart():
    session.pop('cart', None)
    session.modified = True
    return jsonify({'success': True, 'total_items': 0, 'total_price': 0.0, 'items': []}), 200
@cart_api.route('/get_cart', methods=['GET'])
def get_cart():
    summary = get_cart_summary() # Call helper internally
    return jsonify(summary)

def get_cart_summary():
    cart = session.get('cart', {})  # e.g., {'apple_id': 2, 'banana_id': 2}
    items_breakdown = []
    grand_total = 0.0
    total_items_count = 0

    for item_id, qty in cart.items():
        # Query your database model (e.g., SQLAlchemy)
        item = MenuItem.query.get(item_id)
        if not item:
            continue
        
        item_subtotal = item.price * qty
        grand_total += item_subtotal
        total_items_count += qty

        items_breakdown.append({
            'id': item_id,
            'name': item.name,
            'unit_price': item.price,
            'quantity': qty,
            'subtotal': item_subtotal
        })

    return {
        'items': items_breakdown,
        'total_price': grand_total,
        'total_items': total_items_count
    }


@cart_api.route('/update_quantity', methods=['POST'])
def update_quantity():
    data = request.get_json() or {}
    item_id = data.get('item_id')
    new_quantity = data.get('quantity')

    if not item_id or new_quantity is None:
        return jsonify({'success': False, 'message': 'Item ID and quantity required'}), 400

    cart = session.get('cart', {})

    # Update or remove item based on quantity
    if new_quantity > 0:
        cart[item_id] = new_quantity
    else:
        cart.pop(item_id, None)

    session['cart'] = cart
    session.modified = True

    return jsonify({
        'success': True,
        **get_cart_summary()
    }), 200