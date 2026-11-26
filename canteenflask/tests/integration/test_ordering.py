import pytest

from app.extensions import db
from app.models import MenuItem, Order, OrderItem


def add_to_cart(client, item_id):
    return client.post("/api/cart/add_to_cart", data={"item_id": str(item_id)})


def test_order_from_cart_persists_snapshots_and_clears_session(client, app, menu_item):
    assert add_to_cart(client, menu_item).status_code == 200
    assert add_to_cart(client, menu_item).status_code == 200
    summary = client.get("/api/cart/get_cart").get_json()
    assert summary["total_items"] == 2
    assert summary["total_price"] == 7.0
    assert summary["items"][0]["subtotal"] == 7.0

    response = client.post("/api/order/", json={"customer_name": "Test Customer", "customer_phone": "5550000"})
    assert response.status_code == 201
    payload = response.get_json()
    assert payload["total_price"] == 7.0
    assert payload["status"] == "pending"
    assert payload["items"][0]["quantity"] == 2
    assert payload["items"][0]["name"] == "Rice"

    with client.session_transaction() as session:
        assert "cart" not in session
    with app.app_context():
        order = db.session.get(Order, payload["id"])
        assert order.customer_name == "Test Customer"
        assert order.phone == "5550000"
        assert len(order.items) == 1
        assert (order.items[0].item_name, order.items[0].unit_price, order.items[0].quantity) == ("Rice", 3.5, 2)
        item = db.session.get(MenuItem, menu_item)
        item.name, item.price = "Changed name", 9.0
        db.session.commit()
        number = order.order_number

    details = client.get(f"/api/order/{number}")
    assert details.status_code == 200
    assert details.get_json()["items"][0] == {"name": "Rice", "qty": 2, "price": 3.5}
    assert client.get("/order-confirmation/track", query_string={"order_number": number}).status_code == 302


@pytest.mark.parametrize(
    ("cart", "details", "status"),
    [
        ({}, {"customer_name": "Test", "customer_phone": "555"}, 400),
        ({"1": 1}, {"customer_name": "Test"}, 400),
        ({"99999": 1}, {"customer_name": "Test", "customer_phone": "555"}, 404),
    ],
)
def test_invalid_order_does_not_create_order_or_clear_cart(client, app, menu_item, cart, details, status):
    with client.session_transaction() as session:
        session["cart"] = cart
    response = client.post("/api/order/", json=details)
    assert response.status_code == status
    assert response.get_json()["error"]
    with client.session_transaction() as session:
        assert session["cart"] == cart
    with app.app_context():
        assert db.session.query(Order).count() == 0
        assert db.session.query(OrderItem).count() == 0


def test_missing_order_and_cart_update(client, menu_item):
    assert client.get("/api/order/ORD-9999").status_code == 404
    assert client.get("/api/cart/get_cart").get_json() == {"items": [], "total_price": 0.0, "total_items": 0}
    add_to_cart(client, menu_item)
    response = client.post("/api/cart/update_quantity", json={"item_id": str(menu_item), "quantity": 3})
    assert response.status_code == 200
    assert response.get_json()["total_price"] == 10.5
    response = client.post("/api/cart/update_quantity", json={"item_id": str(menu_item), "quantity": 0})
    assert response.get_json()["total_items"] == 0
    assert client.post("/api/cart/update_quantity", json={"item_id": str(menu_item)}).status_code == 400


def test_missing_item_after_valid_item_leaves_no_partial_order(client, app, menu_item):
    cart = {str(menu_item): 2, "99999": 1}
    with client.session_transaction() as session:
        session["cart"] = cart
    response = client.post("/api/order/", json={"customer_name": "Test", "customer_phone": "555"})
    assert response.status_code == 404
    with app.app_context():
        assert db.session.query(Order).count() == 0
        assert db.session.query(OrderItem).count() == 0
    with client.session_transaction() as session:
        assert session["cart"] == cart
