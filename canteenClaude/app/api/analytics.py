"""Analytics API Blueprint.

Provides aggregated sales, performance, and operational metric endpoints
for the canteen administration dashboard. Assumes database timestamps are stored
in local Singapore Time (SGT).
"""

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple

from flask import Blueprint, Response, app, jsonify, request
from app.models import Order  # Adjust model import paths to match your project

analytics_api = Blueprint("analytics_api", __name__)

SG_TZ = timezone(timedelta(hours=8))  # Singapore Timezone (UTC+8)

def _calculate_sgt_time_windows(time_range: str, now: datetime) -> Tuple[datetime, datetime, datetime, datetime]:
    """Calculates local SGT start and end datetime boundaries for database filtering.

    Args:
        time_range (str): Filter parameter ('today', '30d', or default '7d').
        now (datetime): Current naive datetime representing local Singapore Time.

    Returns:
        Tuple[datetime, datetime, datetime, datetime]:
            A 4-element tuple containing local datetimes:
            (start_date, end_date, prev_start, prev_end)
    """
  
    if time_range == "today":
        # Midnight today (00:00:00) to right now
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Mirror exact same timeframe yesterday (00:00:00 yesterday to yesterday same time)
        prev_start = start_date - timedelta(days=1)
        prev_end = end_date - timedelta(days=1)
    elif time_range == "30d":
        start_date = now - timedelta(days=30)
        end_date = now
        
        # Prior 30-day window
        prev_start = now - timedelta(days=60)
        prev_end = start_date
    else:  # Default to '7d'
        start_date = now - timedelta(days=7)
        end_date = now
        
        # Prior 7-day window
        prev_start = now - timedelta(days=14)
        prev_end = start_date

    return start_date, end_date, prev_start, prev_end

@analytics_api.route("/", methods=["GET"])
def get_analytics_data() -> Tuple[Response, int]:
    
    """Retrieves aggregated analytics metrics for the admin dashboard.

    Query Parameters:
        range (str, optional): The target timeframe ('today', '7d', '30d'). Defaults to '7d'.
 
    Returns:
        Tuple[Response, int]: JSON response containing aggregated KPIs, chart datasets,
        and recent orders payload alongside HTTP status 200 (or 500 on failure).
    """
    try:
        time_range: str = request.args.get("range", "today")
        now: datetime = datetime.now(SG_TZ)  # Current local Singapore Time

        start_date, end_date, prev_start, prev_end = _calculate_sgt_time_windows(time_range, now)


        print(f"Start Date: {start_date}, End Date: {end_date}, Prev Start: {prev_start}, Prev End: {prev_end}")
        current_orders: List[Order] = Order.query.filter(
            Order.status.in_(["completed", "ready"]),
            Order.ready_at >= start_date,
            Order.ready_at <= end_date,
        ).all()
        
        prev_orders: List[Order] = Order.query.filter(
            Order.status.in_(["completed", "ready"]),
            Order.created_at >= prev_start,
            Order.created_at < prev_end,
        ).all()
        

        # ----------------------------------------------------------------------
        # 1. KPI Aggregation & Trend Calculations
        # ----------------------------------------------------------------------
        # Check if previous period actually has valid order records
        has_prev_data: bool = len(prev_orders) > 0
        # --- KPI Calculations ---
        revenue: float = round(sum(o.total_price for o in current_orders if o.total_price), 2)
        prev_revenue: float = round(sum(o.total_price for o in prev_orders if o.total_price), 2)
        revenue_trend: str = f"{((revenue - prev_revenue) / prev_revenue * 100):+.1f}%" if prev_revenue else "+0.0%"


        
        orders_completed: int = len(current_orders)
        prev_orders_completed: int = len(prev_orders)
        orders_trend: str = f"{((orders_completed - prev_orders_completed) / prev_orders_completed * 100):+.1f}%" if prev_orders_completed else "+0.0%"


        dishes_completed: int = sum(item.quantity for o in current_orders for item in o.items)
        meals_cooked: int = round(sum(item.quantity for o in current_orders for item in o.items), 2)            
        prev_meals: int = round(sum(item.quantity for o in prev_orders for item in o.items), 2)

        # Order Prep Time Calculation (in minutes)
        prep_times: List[float] = [
            (o.ready_at - o.created_at).total_seconds() / 60.0
            for o in current_orders
            if o.ready_at and o.created_at
        ]

        avg_prep: float = round(sum(prep_times) / len(prep_times), 1) if prep_times else 0.0

        prev_prep_times: List[float] = [
            (o.ready_at - o.created_at).total_seconds() / 60.0
            for o in prev_orders
            if o.ready_at and o.created_at
        ]
        prev_avg_prep: float = round(sum(prev_prep_times) / len(prev_prep_times), 1) if prev_prep_times else 0.0
      
        prep_trend: str = f"{((avg_prep - prev_avg_prep) / prev_avg_prep * 100):+.1f}%" if prev_avg_prep else "+0.0%"
        
        
        # ----------------------------------------------------------------------
        # 2. Dynamic Rush Hours Aggregation (Direct SGT Hour Read)
        # ----------------------------------------------------------------------
        hourly_counts: Dict[int, int] = defaultdict(int)
        for order in current_orders:
            hourly_counts[order.ready_at.hour] += 1
        
        rush_categories: List[str] = []
        rush_data: List[int] = []

        if hourly_counts:
            min_h, max_h = min(hourly_counts.keys()), max(hourly_counts.keys())
            for h in sorted(hourly_counts.keys()):
                label: str = (
                    "12 AM" if h == 0 else f"{h} AM" if h < 12 else "12 PM" if h == 12 else f"{h - 12} PM"
                )
                rush_categories.append(label)
                rush_data.append(hourly_counts[h])
        
     

        # ----------------------------------------------------------------------
        # 3. Top Selling Dishes (Ranked Top 5)
        # ----------------------------------------------------------------------
        dish_counts: Dict[str, int] = defaultdict(int)
        for order in current_orders:
            for item in order.items:
                if item.menu_item:
                    dish_counts[item.menu_item.name] += item.quantity

        sorted_dishes: List[Tuple[str, int]] = sorted(dish_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        
        # ----------------------------------------------------------------------
        # 4. Sales Distribution by Category
        # ----------------------------------------------------------------------
        cat_counts: Dict[str, int] = defaultdict(int)
        for order in current_orders:
            for item in order.items:
                cat_name: str = (
                    item.menu_item.category.name
                    if (item.menu_item and item.menu_item.category)
                    else "Uncategorized"
                )
                cat_counts[cat_name] += item.quantity
        
        # ----------------------------------------------------------------------
        # 5. Recent Completed Orders List
        # ----------------------------------------------------------------------
        # recent_orders_payload: List[Dict[str, Any]] = []
        # sorted_recent: List[Order] = sorted(current_orders, key=lambda x: x.created_at, reverse=True)[:5]

        # for order in sorted_recent:
        #     items_str: str = ", ".join(
        #         [f"{i.menu_item.name} (x{i.quantity})" for i in order.order_items if i.menu_item]
        #     )
        #     recent_orders_payload.append(
        #         {
        #             "id": str(order.id),
        #             "time": order.created_at.strftime("%H:%M"),
        #             "type": getattr(order, "order_type", "Dine-in"),
        #             "table": getattr(order, "table_number", "-"),
        #             "items": items_str,
        #             "amount": float(order.total_price or 0.0),
        #         }
        #     )

        # ----------------------------------------------------------------------
        # 6. Final Response Payload
        # ----------------------------------------------------------------------
        
        payload: Dict[str, Any] = {
                "kpis": {
                    "total_revenue": float(revenue),
                    "orders_completed": orders_completed,
                    "prep_speed": f"{avg_prep:.1f}m",
                    "revenue_trend": revenue_trend,       # Output: "+100%" or "+12.5%"
                    "orders_trend": orders_trend,         # Output: "+100%" or "+12.5%"
                    "prep_trend": prep_trend,           # Output: "+100%" or "+12.5%"


                },
                "rush_hours": {
                    "categories": rush_categories,
                    "series": [{"name": "Orders", "data": rush_data}],
                },
                "top_dishes":{
                    "categories": [d[0] for d in sorted_dishes],
                    "series": [{"name": "Portions Sold", "data": [d[1] for d in sorted_dishes]}],
                },
                "categories": {
                    "labels": list(cat_counts.keys()),
                    "series": list(cat_counts.values()),
                },
        }
        
        # payload: Dict[str, Any] = {
        #     "kpis": {
        #         "total_revenue": float(revenue),
        #         "revenue_trend": revenue_trend_str,       # Output: "+100%" or "+12.5%"
        #         "meals_cooked": meals_cooked,
        #         "meals_trend": meals_trend_str,           # Output: "+100%" or "-5.0%"
        #         "prep_speed": f"{avg_prep:.1f}m",
        #         "prep_trend": prep_trend_str,
        #     },
        #     "rush_hours": {
        #         "categories": rush_categories,
        #         "series": [{"name": "Orders", "data": rush_data}],
        #     },
        #     "top_dishes": {
        #         "categories": [d[0] for d in sorted_dishes],
        #         "series": [{"name": "Portions Sold", "data": [d[1] for d in sorted_dishes]}],
        #     },
        #     "categories": {
        #         "labels": list(cat_counts.keys()),
        #         "series": list(cat_counts.values()),
        #     },
        #     "recent_orders": recent_orders_payload,
        # }

        return jsonify(payload), 200

    except Exception as err:
        return jsonify({"error": "Internal server error processing analytics", "details": str(err)}), 500


@analytics_api.route("/revenue", methods=["GET"])
def update_revenue():
    try:
        time_range = request.args.get("range", "7d")
        now = datetime.now(SG_TZ)
        start_date, end_date, prev_start, prev_end = _calculate_sgt_time_windows(time_range, now)

        current_orders = Order.query.filter(
            Order.status.in_(["completed", "ready"]),
            Order.ready_at >= start_date,
            Order.ready_at <= end_date,
        ).all()
        previous_orders = Order.query.filter(
            Order.status.in_(["completed", "ready"]),
            Order.ready_at >= prev_start,
            Order.ready_at < prev_end,
        ).all()

        revenue = round(sum(float(order.total_price or 0) for order in current_orders), 2)
        previous_revenue = sum(float(order.total_price or 0) for order in previous_orders)
        revenue_trend = (
            f"{((revenue - previous_revenue) / previous_revenue * 100):+.1f}%"
            if previous_revenue else "+0.0%"
        )
        
        print(f"Revenue: {revenue}, Revenue Trend: {revenue_trend}")

        return f"""
            <div id="revenue-kpi" hx-swap-oob="true">${revenue}</div>
            <div id="revenue-trend-kpi" hx-swap-oob="true">{revenue_trend}</div>
        """

    except Exception as err:
        return jsonify({"error": "Internal server error processing revenue", "details": str(err)}), 500