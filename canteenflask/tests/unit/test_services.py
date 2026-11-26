from datetime import datetime

import pytest
from flask import session

from app.admin.routes import calculate_pagination_window
from app.api.analytics import _calculate_sgt_time_windows
from app.models import User
from app.services.analytics_service import calculate_trend
from app.services.cart_service import adjust_item_quantity, get_total_items
from app.services.order_service import format_order_number


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("", None), ("  0450  ", "ORD-0450"), ("ORD-0450", "ORD-0450"),
     ("ord-45", "ORD-45")],
)
def test_format_order_number(raw, expected):
    assert format_order_number(raw) == expected


@pytest.mark.parametrize(
    ("current", "previous", "expected"),
    [(0, 0, "0.0%"), (10, 0, "+100.0%"), (15, 10, "+50.0%"),
     (5, 10, "-50.0%"), (10, 10, "+0.0%")],
)
def test_calculate_trend(current, previous, expected):
    assert calculate_trend(current, previous) == expected


@pytest.mark.parametrize(
    ("current", "total", "expected"),
    [(1, 0, []), (1, 3, [1, 2, 3]), (1, 10, [1, 2, 3, 4, 5]),
     (5, 10, [3, 4, 5, 6, 7]), (10, 10, [6, 7, 8, 9, 10])],
)
def test_pagination_window(current, total, expected):
    assert list(calculate_pagination_window(current, total)) == expected


@pytest.mark.parametrize(
    ("period", "expected_start", "expected_end", "previous_start", "previous_end"),
    [
        ("today", datetime(2026, 3, 1), datetime(2026, 3, 1, 23, 59, 59, 999999),
         datetime(2026, 2, 28), datetime(2026, 2, 28, 23, 59, 59, 999999)),
        ("7d", datetime(2026, 2, 22, 12), datetime(2026, 3, 1, 12),
         datetime(2026, 2, 15, 12), datetime(2026, 2, 22, 12)),
        ("30d", datetime(2026, 1, 30, 12), datetime(2026, 3, 1, 12),
         datetime(2025, 12, 31, 12), datetime(2026, 1, 30, 12)),
    ],
)
def test_analytics_time_windows(period, expected_start, expected_end, previous_start, previous_end):
    assert _calculate_sgt_time_windows(period, datetime(2026, 3, 1, 12)) == (
        expected_start, expected_end, previous_start, previous_end
    )


def test_cart_quantity_and_count(app):
    with app.test_request_context():
        assert get_total_items() == 0
        assert adjust_item_quantity(42, 2) == 2
        assert adjust_item_quantity(7, 1) == 1
        assert get_total_items() == 3
        assert adjust_item_quantity(42, -1) == 1
        assert adjust_item_quantity(42, -2) == 0
        assert session["cart"] == {"7": 1}
        assert get_total_items() == 1


def test_password_verification():
    user = User(username="sample", email="sample@example.test")
    user.set_password("correct-password")
    assert user.check_password("correct-password")
    assert not user.check_password("incorrect-password")
