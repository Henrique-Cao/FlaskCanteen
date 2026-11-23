from flask import session
from app.models import MenuItem


def adjust_item_quantity(item_id: int, delta: int) -> int:
    """Adds or subtracts item quantity in the session cart. Removes item at 0."""
    cart = session.get("cart", {})
    key = str(item_id)

    new_qty = int(cart.get(key, 0)) + delta
    if new_qty <= 0:
        cart.pop(key, None)
        new_qty = 0
    else:
        cart[key] = new_qty

    session["cart"] = cart
    session.modified = True
    return new_qty


def get_total_items() -> int:
    """Returns total item count directly from session (no DB query)."""
    cart = session.get("cart", {})
    return sum(int(qty) for qty in cart.values())



def get_cart_summary() -> dict:
    """Fetches current DB prices and calculates subtotals and cart total."""
    cart = session.get("cart", {})
    if not cart:
        return {"cart_items": [], "total": 0.0, "total_items": 0}

    item_ids = [int(k) for k in cart.keys()]
    db_items = MenuItem.query.filter(MenuItem.id.in_(item_ids)).all()
    item_lookup = {item.id: item for item in db_items}

    cart_items = []
    total_price = 0.0
    total_items = 0

    for key, qty in cart.items():
        menu_item = item_lookup.get(int(key))
        if not menu_item:
            continue

        qty = int(qty)
        subtotal = float(menu_item.price) * qty
        total_price += subtotal
        total_items += qty

        cart_items.append({
            "id": menu_item.id,
            "name": menu_item.name,
            "price": float(menu_item.price),
            "quantity": qty,
            "subtotal": round(subtotal, 2),
        })

    return {
        "cart_items": cart_items,
        "total": round(total_price, 2),
        "total_items": total_items,
    }