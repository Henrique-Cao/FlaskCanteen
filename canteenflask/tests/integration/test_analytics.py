from datetime import datetime

from werkzeug.datastructures import MultiDict

import app.api.analytics as analytics_api
import app.services.analytics_service as analytics_service
from app.extensions import db
from app.models import Order, OrderItem
from app.services.order_service import get_filtered_orders_query


class FixedDatetime(datetime):
    @classmethod
    def now(cls, tz=None):
        return cls(2026, 3, 1, 12, 0, tzinfo=tz)


def make_order(number, status, created, total, menu_item, ready=None, quantity=1):
    order = Order(
        order_number=number, customer_name=f"Customer {number}", phone=f"555{number[-1]}",
        status=status, created_at=created, ready_at=ready, total_price=total,
    )
    order.items.append(OrderItem(menu_item_id=menu_item, item_name="Rice", unit_price=3.5, quantity=quantity))
    return order


def test_order_filters_combine_search_status_date_and_price(app, menu_item):
    with app.app_context():
        db.session.add_all([
            make_order("ORD-0001", "completed", datetime(2026, 2, 28, 23), 7, menu_item),
            make_order("ORD-0002", "completed", datetime(2026, 3, 1, 8), 14, menu_item),
            make_order("ORD-0003", "pending", datetime(2026, 3, 1, 10), 20, menu_item),
            make_order("ORD-0004", "completed", datetime(2026, 3, 2, 8), 18, menu_item),
        ])
        db.session.commit()
        args = MultiDict([
            ("q", "Customer"), ("status", "completed"), ("start_date", "2026-03-01"),
            ("end_date", "2026-03-01"), ("min_price", "10"), ("max_price", "15"),
        ])
        assert [order.order_number for order in get_filtered_orders_query(args).all()] == ["ORD-0002"]
        assert [order.order_number for order in get_filtered_orders_query(MultiDict([("q", "5553")])).all()] == ["ORD-0003"]
        assert get_filtered_orders_query(MultiDict([("q", "not present")])).all() == []
        assert [order.order_number for order in get_filtered_orders_query(MultiDict()).all()] == [
            "ORD-0004", "ORD-0003", "ORD-0002", "ORD-0001"
        ]


def test_dashboard_service_counts_completed_orders_within_day(app, menu_item, monkeypatch):
    monkeypatch.setattr(analytics_service, "datetime", FixedDatetime)
    with app.app_context():
        db.session.add_all([
            make_order("ORD-0001", "completed", datetime(2026, 3, 1, 8), 7, menu_item,
                       ready=datetime(2026, 3, 1, 8, 10), quantity=2),
            make_order("ORD-0002", "pending", datetime(2026, 3, 1, 9), 3.5, menu_item),
            make_order("ORD-0003", "completed", datetime(2026, 3, 2), 3.5, menu_item),
        ])
        db.session.commit()
        metrics = analytics_service.get_dashboard_metrics("today")
        assert metrics["kpi"]["revenue"] == 7
        assert metrics["kpi"]["meals"] == 2
        assert metrics["kpi"]["prep"] == 10
        assert sum(metrics["chart_revenue"]) == 7
        assert sum(metrics["chart_traffic"]) == 1
        assert metrics["top_items"][0]["name"] == "Rice"
        assert metrics["top_items"][0]["sold"] == 2
        assert metrics["top_categories"][0]["name"] == "Meals"


def test_analytics_api_empty_and_ready_orders(client, app, menu_item, monkeypatch):
    monkeypatch.setattr(analytics_api, "datetime", FixedDatetime)
    empty = client.get("/api/analytics/?range=today")
    assert empty.status_code == 200
    assert empty.get_json()["kpis"]["total_revenue"] == 0
    assert empty.get_json()["top_dishes"]["categories"] == []

    with app.app_context():
        db.session.add_all([
            make_order("ORD-0001", "ready", datetime(2026, 3, 1, 8), 7, menu_item,
                       ready=datetime(2026, 3, 1, 8, 10), quantity=2),
            make_order("ORD-0002", "pending", datetime(2026, 3, 1, 9), 3.5, menu_item),
        ])
        db.session.commit()
    response = client.get("/api/analytics/?range=today")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["kpis"]["total_revenue"] == 7
    assert payload["kpis"]["orders_completed"] == 1
    assert payload["kpis"]["prep_speed"] == "10.0m"
    assert payload["rush_hours"]["categories"] == ["8 AM"]
    assert payload["top_dishes"]["categories"] == ["Rice"]
    assert payload["top_dishes"]["series"][0]["data"] == [2]
    assert payload["categories"] == {"labels": ["Meals"], "series": [2]}
