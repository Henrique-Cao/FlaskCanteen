from datetime import datetime, timedelta

import pytest

from app.extensions import db
from app.models import MenuItem, Order, User


ADMIN_PAGES = ["/admin/", "/admin/manage-menu", "/admin/orders", "/admin/history", "/admin/analytics/content"]


@pytest.mark.parametrize("path", ADMIN_PAGES)
def test_admin_pages_reject_unauthenticated_and_non_admin_users(client, app, path):
    response = client.get(path)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")
    assert client.get(path, headers={"Content-Type": "application/json"}).status_code == 401

    with app.app_context():
        user = User(username="customer", email="customer@example.test", role="customer")
        user.set_password("test-password")
        db.session.add(user)
        db.session.commit()
    assert client.post("/api/auth/login", json={"username": "customer", "password": "test-password"}).status_code == 200
    assert client.get(path).status_code == 403
    assert client.get(path, headers={"Content-Type": "application/json"}).status_code == 403


def test_admin_menu_page_displays_categorized_and_uncategorized_items(admin_client, app, menu_item):
    with app.app_context():
        db.session.add(MenuItem(name="Tea", price=2.0))
        db.session.commit()
    response = admin_client.get("/admin/manage-menu")
    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "Meals" in page
    assert "Rice" in page
    assert "Tea" in page


@pytest.fixture
def history_orders(app):
    with app.app_context():
        for i in range(1, 13):
            db.session.add(Order(
                order_number=f"ORD-{i:04d}", customer_name=f"Customer {i}", phone=f"555{i:04d}",
                status="completed", total_price=float(i), created_at=datetime(2026, 3, 1) + timedelta(hours=i),
            ))
        db.session.add(Order(
            order_number="ORD-9999", customer_name="Pending Customer", phone="5559999",
            status="pending", total_price=99, created_at=datetime(2026, 3, 2),
        ))
        db.session.commit()


def test_order_history_page_filters_and_paginates(admin_client, history_orders):
    first = admin_client.get("/admin/history")
    assert first.status_code == 200
    assert "Order History" in first.get_data(as_text=True)
    assert "ORD-0012" in first.get_data(as_text=True)
    assert "ORD-0001" not in first.get_data(as_text=True)
    assert "ORD-9999" not in first.get_data(as_text=True)

    second = admin_client.get("/admin/history?page=2")
    assert second.status_code == 200
    assert "ORD-0001" in second.get_data(as_text=True)
    assert "ORD-0012" not in second.get_data(as_text=True)

    filtered = admin_client.get("/admin/history", query_string={"q": "ORD-0003"}, headers={"HX-Request": "true"})
    assert filtered.status_code == 200
    assert 'id="historyTable"' in filtered.get_data(as_text=True)
    assert "ORD-0003" in filtered.get_data(as_text=True)
    assert "ORD-0004" not in filtered.get_data(as_text=True)
    assert "<html" not in filtered.get_data(as_text=True).lower()


def test_admin_orders_and_analytics_pages_render(admin_client):
    orders = admin_client.get("/admin/orders")
    assert orders.status_code == 200
    assert "Active Orders" in orders.get_data(as_text=True)
    analytics = admin_client.get("/admin/analytics/content?range=7d")
    assert analytics.status_code == 200
    assert "Last 7 Days Revenue Trend" in analytics.get_data(as_text=True)
    assert "Total Revenue" in analytics.get_data(as_text=True)
