# app/routes/order.py
from flask import Blueprint, jsonify, request, session, url_for
from app.extensions import db
from app.models import MenuItem, Order, OrderItem
from datetime import datetime, timedelta, timezone


# Singapore is permanently fixed at UTC+8
SG_TZ = timezone(timedelta(hours=8))

order_api = Blueprint('order_api', __name__)

# Create a new order from the session cart and customer details
@order_api.route('/', methods=['POST'])
def create_order():
    data = request.get_json() or {}
    cart = session.get('cart', {})

    # 1. Ensure the session cart is not empty
    if not cart:
        return jsonify({"error": "Your cart is empty."}), 400

    # 2. Extract customer details (fall back to verified_phone from session if present)
    customer_name = data.get('customer_name')
    phone = data.get('phone') or session.get('verified_phone')

    if not customer_name or not phone:
        return jsonify({"error": "Missing required fields: 'customer_name' and 'phone' are mandatory."}), 400

    existing_order_numbers = Order.query.with_entities(Order.order_number).all()
    highest_order_number = max(
        (
            int(order_number.removeprefix('ORD-'))
            for (order_number,) in existing_order_numbers
            if order_number.startswith('ORD-')
            and order_number.removeprefix('ORD-').isdigit()
        ),
        default=0
    )
    order_number = f"ORD-{highest_order_number + 1:04d}"
    # 3. Create the base Order instance
    new_order = Order(
        order_number=order_number,
        customer_name=customer_name,
        phone=phone,
        status=Order.STATUS_PENDING,
        total_price=0.0
    )

    total_price = 0.0

    # 4. Read directly from session['cart'] ({item_id: quantity})
    for item_id, quantity in cart.items():
        menu_item = MenuItem.query.get(item_id)
        if not menu_item:
            return jsonify({"error": f"Menu item with ID {item_id} not found."}), 404

        order_item = OrderItem(
            menu_item_id=menu_item.id,
            quantity=quantity,
            unit_price=menu_item.price,  # Snapshot price at time of order
            item_name=menu_item.name

        )
        new_order.items.append(order_item)
        total_price += quantity * float(menu_item.price)
    new_order.total_price = total_price

    # 5. Commit order to database
    db.session.add(new_order)
    db.session.commit()

    # 6. Clear session cart after successful order creation
    session.pop('cart', None)
    session.modified = True

    # 7. Return success payload with confirmation URL for JS navigation
    return jsonify({
        "success": True,
        "id": new_order.id,
        "customer_name": new_order.customer_name,
        "total_price": float(new_order.total_price),
        "status": new_order.status,
        "created_at": new_order.created_at.isoformat(),
        "redirect_url": f"/confirmation/{new_order.order_number}",
        "items": [
            {
                "menu_item_id": item.menu_item_id,
                "quantity": item.quantity,
                "price": float(item.unit_price),
                "name": item.menu_item.name,
                "order_number": order_number
            } for item in new_order.items
        ]
    }), 201

# Get all orders (for admin view)
@order_api.route('/', methods=['GET'])
def get_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify([{
        "id": order.id,
        "order_number": order.order_number,
        "customer_name": order.customer_name,
        "phone": order.phone,
        "status": order.status,
        "total_price": float(order.total_price),
        "created_at": order.created_at.isoformat(),
        "items": [
            {
                "menu_item_id": item.menu_item_id,
                "quantity": item.quantity,
                "price": float(item.unit_price),
                "name": item.menu_item.name
            } for item in order.items
        ]
    } for order in orders]), 200

@order_api.route('/active', methods=['GET'])
def get_active_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    print(orders)
    return jsonify([{
        "id": order.id,
        "order_number": order.order_number,
        "customer_name": order.customer_name,
        "phone": order.phone,
        "status": order.status,
        "total_price": float(order.total_price),
        "created_at": order.created_at.isoformat(),
        "items": [
            {
                "menu_item_id": item.menu_item_id,
                "quantity": item.quantity,
                "price": float(item.unit_price),
                "name": item.menu_item.name
            } for item in order.items
        ]
    } for order in orders]), 200

@order_api.route('/<string:order_number>', methods=['GET'])
def get_order_details(order_number):
  
    order = Order.query.filter_by(order_number=order_number).first_or_404()

    return jsonify({
        "orderNumber": order.order_number,
        "time": order.created_at.strftime("%I:%M %p") if order.created_at else "--:--",
        "customer": order.customer_name or "N/A",
        "phone": order.phone or "N/A",
        "status": order.status,
        "total": order.total_price,
        "items": [
            {
                "name": item.item_name or getattr(item, 'item_name', None) or "Item",
                "qty": item.quantity or 1,
                "price": float(item.unit_price or 0.0)
            } for item in order.items
        ]
    })

# modify order status (for admin)
@order_api.route('/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    print(f"Received request to update status for order ID: {order_id}")
    data = request.get_json() or {}
    new_status = data.get('status')

    if new_status not in [Order.STATUS_PENDING, Order.STATUS_CONFIRMED, Order.STATUS_READY, Order.STATUS_COMPLETED]:
        return jsonify({"error": "Invalid status value."}), 400

    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found."}), 404

    
    order.status = new_status
    if new_status == Order.STATUS_READY:
        order.ready_at = datetime.now(SG_TZ)



    db.session.commit()

    return jsonify({
        "success": True,
        "id": order.id,
        "order_number": order.order_number,
        "status": order.status
    }), 200

# mark order as completed (for admin)
@order_api.route('/<int:order_id>/complete', methods=['PUT'])
def complete_order(order_id):
    print(f"Attempting to mark order ID {order_id} as completed")
    order = Order.query.get(order_id)
    print(f"Received request to mark order ID {order_id} as completed")
    if not order:
        return jsonify({"error": "Order not found."}), 404

    order.status = Order.STATUS_COMPLETED
    order.completed_at = datetime.now(SG_TZ)
    db.session.commit()

    return jsonify({
        "success": True,
        "id": order.id,
        "order_number": order.order_number,
        "status": order.status
    }), 200

@order_api.route('/<int:order_id>/cancel', methods=['PUT'])
def cancel_order(order_id):
    print(f"Attempting to cancel order ID {order_id}")
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found."}), 404

    order.status = Order.STATUS_CANCELLED
    order.cancelled_at = datetime.now(SG_TZ)
    db.session.commit()

    return jsonify({
        "success": True,
        "id": order.id,
        "order_number": order.order_number,
        "status": order.status
    }), 200