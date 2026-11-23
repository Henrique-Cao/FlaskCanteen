from flask import Blueprint, render_template, request, session
from app.models import MenuItem
from app.services import cart_service

cart_bp = Blueprint("cart", __name__, url_prefix="/cart")


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
    print("loading items")
    return render_template("partials/_cart_items.html", **cart_service.get_cart_summary())