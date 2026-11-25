from datetime import datetime, timezone

from flask import Blueprint, redirect, render_template, request, url_for
from sqlalchemy import or_
from app.models import MenuItem, Order, OrderItem
order_confirmation_bp = Blueprint("order_confirmation", __name__)


@order_confirmation_bp.app_template_filter("timeago")
def timeago(value):
    """Format a datetime as a human-readable relative time."""
    if not isinstance(value, datetime):
        return ""

    now = datetime.now(value.tzinfo) if value.tzinfo else datetime.now()
    seconds = max(0, int((now - value).total_seconds()))
    if seconds < 60:
        return "just now"
    if seconds < 3600:
        amount, unit = seconds // 60, "minute"
    elif seconds < 86400:
        amount, unit = seconds // 3600, "hour"
    elif seconds < 604800:
        amount, unit = seconds // 86400, "day"
    elif seconds < 2592000:
        amount, unit = seconds // 604800, "week"
    elif seconds < 31536000:
        amount, unit = seconds // 2592000, "month"
    else:
        amount, unit = seconds // 31536000, "year"

    return f"{amount} {unit}{'' if amount == 1 else 's'} ago"
 



@order_confirmation_bp.route("/track")
def track():
   
    raw_q = request.args.get("order_number", "").strip()
    clean_q = raw_q.lstrip("#")  # Handles both "#ORD-0450" and "ORD-0450"
    print(f"Raw query: {raw_q}, Clean query: {clean_q}")
    if not clean_q:
        return redirect(url_for("main.index"))  # Adjust to your home blueprint endpoint

    # Match exact order number (case-insensitive) OR phone number (newest order first)
    order = (
        Order.query.filter(or_(
                Order.order_number.ilike(clean_q),
                Order.phone.ilike(f"%{clean_q}%")
            )
        )
        .order_by(Order.created_at.desc())
        .first()
    )
    
    if order:
        return redirect(
            url_for("order_confirmation.index", order_number=order.order_number)
        )

    total_amount = 0
    if order:
        total_amount = sum(item.quantity * item.unit_price for item in OrderItem.query.filter_by(order_id=order.id).all())
    # Reuses your existing confirmation template's empty/not-found state
    return render_template(
        "order_confirmation/order_confirmation.html",
        order=None,
        order_items=[],
        order_number=raw_q,
        items_with_details=[],
        total_amount = total_amount
    )


@order_confirmation_bp.route("/<order_number>")
def index(order_number):
    
    clean_number = order_number.strip().lstrip("#")

    order = Order.query.filter(Order.order_number.ilike(clean_number)).first()
    print(order)
    order_items = []
    items_with_details = []
    total_amount = 0
    now = datetime.now(order.created_at.tzinfo) if order and order.created_at.tzinfo else datetime.now()
    print("order", order)
    if order:
        # Single JOIN query instead of querying MenuItem inside a loop
        results = (
            OrderItem.query.join(MenuItem, OrderItem.menu_item_id == MenuItem.id)
            .add_entity(MenuItem)
            .filter(OrderItem.order_id == order.id)
            .all()
        )

        for order_item, menu_item in results:
            order_items.append(order_item)
            items_with_details.append({
                "name": menu_item.name,
                "quantity": order_item.quantity,
                "unit_price": order_item.unit_price,
                "total_price": order_item.quantity * order_item.unit_price,
            })

    total_amount = sum(item["total_price"] for item in items_with_details)
    elapsed_time_mins = (now - order.created_at).total_seconds() / 60 if order else None
    return render_template(
        "order_confirmation/order_confirmation.html",
        order=order,
        order_items=order_items,
        order_number=order.order_number if order else clean_number,
        items_with_details=items_with_details,
        total_amount=total_amount,
        elapsed_time_mins=elapsed_time_mins
    )

@order_confirmation_bp.route("/<int:order_id>/status", methods=["GET"])
def order_status_partial(order_id):
    order = Order.query.get_or_404(order_id)
    print(order)
    order_status = order.status
    if order_status == 'pending':
        order.status = 'preparing'
    return render_template("partials/_order_status_card.html", order=order, order_status=order_status)
# @order_confirmation_bp.route("/<order_number>")
# def index(order_number):
#     # get the order details from the database using the order_number
#     order = Order.query.filter_by(order_number=order_number).first()
#     order_items = OrderItem.query.filter_by(order_id=order.id).all() if order else []
#     items_with_details = []
#     for item in order_items:
#         menu_item = MenuItem.query.get(item.menu_item_id)
#         if menu_item:
#             items_with_details.append({
#                 "name": menu_item.name,
#                 "quantity": item.quantity,
#                 "unit_price": item.unit_price,
#                 "total_price": item.quantity * item.unit_price
#             })
        
#     return render_template("order_confirmation/order_confirmation.html", order=order, order_items=order_items, order_number=order_number, items_with_details=items_with_details )




 