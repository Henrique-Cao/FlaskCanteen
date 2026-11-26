from flask import Blueprint, make_response, render_template, request, session,url_for
from app.models import MenuItem
from app.services import cart_service
from app.api.order import create_order


cart_bp = Blueprint("cart", __name__, url_prefix="/cart")

@cart_bp.route("/", methods=["GET"])
def get_cart():
    return render_template("partials/_cart.html", **cart_service.get_cart_summary())

@cart_bp.route("/update/<int:item_id>", methods=["POST"])
def update_cart(item_id):
    MenuItem.query.get_or_404(item_id)
    delta = request.form.get("delta", 1, type=int)
    cart_service.adjust_item_quantity(item_id, delta)
    # 204 returns no HTML; HX-Trigger tells the badge and modal to refresh themselves
    return "", 204, {"HX-Trigger": "cartUpdated"}

@cart_bp.route("/clear", methods=["POST"])
def clear_cart():
    session.pop("cart", None)
    session.modified = True
    return "", 204, {"HX-Trigger": "cartUpdated"}

@cart_bp.route("/count", methods=["GET"])
def cart_count():
    count = cart_service.get_total_items()
    return str(count) if count > 0 else ""


@cart_bp.route("/modal", methods=["GET"])
def cart_modal():
    return render_template("partials/_cart_items.html", **cart_service.get_cart_summary())

@cart_bp.route("/checkout", methods=["GET"])
def checkout():
    # try:
    #     order = create_order(
    #         customer_name=request.form.get("customer_name", "").strip(),
    #         phone=request.form.get("phone", "").strip(),
    #         cart_items=cart_service.get_cart_items(),
    #     )
    # except ValueError as err:
    #     # Stays on the same page and swaps the error into #checkout-error
    #     return f'<div class="alert alert-danger py-2 small">{err}</div>'

    # cart_service.clear_cart()

    # # Route handles directing the browser to the confirmation page
    # response = make_response("", 200)
    # response.headers["HX-Redirect"] = url_for(
    #     "order_confirmation.index",
    #     order_number=order.order_number,
    # )
    # return response
    return