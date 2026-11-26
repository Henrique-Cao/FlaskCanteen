from datetime import datetime

import pytest

from app.extensions import db
from app.models import Order, OrderItem


@pytest.fixture
def order(app, menu_item):
    with app.app_context():
        order = Order(
            order_number="ORD-0042", customer_name="Test Customer", phone="5550042",
            total_price=7.0, status="pending", created_at=datetime(2026, 3, 1, 8),
        )
        order.items.append(OrderItem(menu_item_id=menu_item, item_name="Rice", quantity=2, unit_price=3.5))
        db.session.add(order)
        db.session.commit()
        return order.id


@pytest.mark.parametrize("path", ["/confirmation/ORD-0042", "/order-confirmation/ord-0042"])
def test_confirmation_displays_order_and_line_total(client, order, path):
    response = client.get(path)
    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "ORD-0042" in page
    assert "Test Customer" in page
    assert "Rice" in page
    assert "2x" in page
    assert "$7.00" in page


@pytest.mark.parametrize("query", ["#ord-0042", "5550042"])
def test_tracking_redirects_to_matching_order(client, order, query):
    response = client.get("/order-confirmation/track", query_string={"order_number": query})
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/order-confirmation/ORD-0042")


def test_tracking_empty_and_unknown_order(client):
    empty = client.get("/order-confirmation/track")
    assert empty.status_code == 302
    assert empty.headers["Location"].endswith("/")
    missing = client.get("/order-confirmation/track", query_string={"order_number": "ORD-9999"})
    assert missing.status_code == 200
    assert "Order not found or unavailable." in missing.get_data(as_text=True)
    page = client.get("/order-confirmation/ORD-9999")
    assert page.status_code == 200
    assert "Order not found or unavailable." in page.get_data(as_text=True)
    assert client.get("/confirmation/ORD-9999").status_code == 404


def test_order_status_partial_reflects_status_without_persisting_changes(client, app, order):
    response = client.get(f"/order-confirmation/{order}/status")
    assert response.status_code == 200
    assert "Chef is cooking" in response.get_data(as_text=True)
    with app.app_context():
        stored = db.session.get(Order, order)
        assert stored.status == "pending"
        stored.status = "ready"
        db.session.commit()
    response = client.get(f"/order-confirmation/{order}/status")
    assert response.status_code == 200
    assert "ready at the pickup counter" in response.get_data(as_text=True)
    assert client.get("/order-confirmation/99999/status").status_code == 404
