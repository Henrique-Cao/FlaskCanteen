# app/routes/order.py
from flask import Blueprint, jsonify, request, session, url_for
from app.extensions import db
from app.models import MenuItem, Order, OrderItem
import uuid
order_api = Blueprint('order_api', __name__)

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

    order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
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
            unit_price=menu_item.price  # Snapshot price at time of order
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
        "redirect_url": f"/order/{new_order.id}",
        "items": [
            {
                "menu_item_id": item.menu_item_id,
                "quantity": item.quantity,
                "price": float(item.unit_price)
            } for item in new_order.items
        ]
    }), 201