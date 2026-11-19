from datetime import datetime, timedelta
from sqlalchemy import func, desc
from app.models import db, Order, OrderItem, MenuItem, Category

def calculate_trend(current, previous):
    """Helper to calculate percentage changes safely."""
    if previous == 0:
        return "+100.0%" if current > 0 else "0.0%"
    change = ((current - previous) / previous) * 100
    sign = "+" if change >= 0 else ""
    return f"{sign}{change:.1f}%"

def get_top_selling_items(start_date, end_date, limit=5):
    # Query your top items ordered by total_sold descending
    top_items = db.session.query(
        MenuItem.name,
        func.sum(OrderItem.quantity).label('total_sold')
    ).select_from(OrderItem).join(Order).join(MenuItem).filter(
        Order.created_at >= start_date,
        Order.created_at < end_date,
        Order.status == 'completed'
    ).group_by(MenuItem.id).order_by(
        desc('total_sold')
    ).limit(limit).all()

    if not top_items:
        return []

    # The first item has the highest sales due to the descending order
    max_sales = float(top_items[0].total_sold)
    
    distribution_list = []
    for item in top_items:
        # Calculate width relative to the #1 seller
        relative_width = (float(item.total_sold) / max_sales) * 100 if max_sales > 0 else 0
        
        distribution_list.append({
            'name': item.name,
            'sold': item.total_sold,
            'width_percent': round(relative_width)
        })
        
    return distribution_list

def get_top_category(start_date, end_date, limit=5):
    # Query your top categories ordered by total_sold descending
    top_categories = db.session.query(
        MenuItem.category_id,
        Category.name.label('category_name'),
        func.sum(OrderItem.quantity).label('total_sold')
    ).select_from(OrderItem).join(Order).join(MenuItem).filter(
        Order.created_at >= start_date,
        Order.created_at < end_date,
        Order.status == 'completed'
    ).join(Category, MenuItem.category_id == Category.id).group_by(
        MenuItem.category_id, Category.name
    ).order_by(
        desc('total_sold')
    ).limit(limit).all()

    if not top_categories:
        return []

    max_sales = float(top_categories[0].total_sold)
    
    distribution_list = []
    for item in top_categories:
        relative_width = (float(item.total_sold) / max_sales) * 100 if max_sales > 0 else 0
        distribution_list.append({
            'category': item.category_id,
            'name': item.category_name,
            'sold': item.total_sold,
            'width_percent': round(relative_width)
        })
        
    return distribution_list



def get_dashboard_metrics(date_range='today'):
    """Calculates all KPIs and chart arrays for the dashboard."""
    now = datetime.now()
    buckets = {}
    # 1. Setup Time Boundaries
    if date_range == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
        prev_start = start_date - timedelta(days=1)
        prev_end = start_date

        for h in range(0, 24):
            hour_str = f"{h:02d}" # '11', '12', '13'...
            label = f"{h if h <= 12 else h - 12} {'AM' if h < 12 else 'PM'}"
            buckets[hour_str] = {
                'label': label, 
                'revenue': 0.0, 
                'traffic': 0
            }
        sql_date_format = '%H'
    elif date_range == '7d':
        start_date = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
        prev_start = start_date - timedelta(days=7)
        prev_end = start_date
        end_date = now

        for i in range(7):
            day = start_date + timedelta(days=i)
            day_str = day.strftime('%Y-%m-%d')
            buckets[day_str] = {
                'label': day.strftime('%a'), # 'Mon', 'Tue', etc.
                'revenue': 0.0, 
                'traffic': 0
            }
        sql_date_format = '%Y-%m-%d'
    else:
        # All time
        start_date = datetime.min
        prev_start = None
        prev_end = None
        
        sql_date_format = '%Y-%m-%d'
        # Initialize buckets for all time by day
        # We'll fill them dynamically as we encounter orders
        buckets = {}


    chart_stats = db.session.query(
        func.strftime(sql_date_format, Order.created_at).label('time_bucket'),
        func.sum(Order.total_price).label('total_revenue'),
        func.count(Order.id).label('total_traffic')
    ).filter(
        Order.created_at >= start_date,
        Order.created_at < end_date,
        Order.status == 'completed'
    ).group_by('time_bucket').all()
    
    # Pour SQL Results into our empty buckets
    for stat in chart_stats:
        bucket_key = stat.time_bucket
        if bucket_key in buckets:
            buckets[bucket_key]['revenue'] = float(stat.total_revenue or 0)
            buckets[bucket_key]['traffic'] = int(stat.total_traffic or 0)

    # Hide hours before the first order today so the chart starts when the
    # store becomes active and after its last order. Keep all hours when there
    # are no orders yet.
    if date_range == 'today':
        active_hours = [
            hour for hour, bucket in buckets.items()
            if bucket['traffic'] > 0
        ]
        if active_hours:
            first_active_hour = active_hours[0]
            last_active_hour = active_hours[-1]
            buckets = {
                hour: bucket
                for hour, bucket in buckets.items()
                if first_active_hour <= hour <= last_active_hour
            }

    # ---------------------------------------------------------
    # 3. Calculate Current & Previous Meals (Requires OrderItem Join)
    # ---------------------------------------------------------
    current_meals = db.session.query(func.sum(OrderItem.quantity)).join(Order).filter(
        Order.created_at >= start_date,
        Order.status == 'completed'
    ).scalar() or 0

    prev_stats = db.session.query(
        func.sum(Order.total_price).label('revenue'),
        func.sum(OrderItem.quantity).label('meals')
    ).select_from(OrderItem).join(Order).filter(
        Order.created_at >= prev_start,
        Order.created_at < prev_end,
        Order.status == 'completed'
    ).first()

    prev_revenue = float(prev_stats.revenue or 0)
    prev_meals = int(prev_stats.meals or 0)

    # ---------------------------------------------------------
    # 4. Calculate Average Prep Speed
    # ---------------------------------------------------------
    completed_orders = Order.query.filter(
        Order.created_at >= start_date,
        Order.status == 'completed'
    ).all()
    
    if completed_orders and hasattr(Order, 'ready_at'):
        prep_times = [
            (o.ready_at - o.created_at).total_seconds()
            for o in completed_orders
            if o.ready_at is not None
        ]
        if prep_times:
            avg_prep_mins = (sum(prep_times) / len(prep_times)) / 60
        else:
            avg_prep_mins = 0.0
    else:
        avg_prep_mins = 0.0
    
    # avg prep for previous period (if needed)
    prev_avg_prep_mins = 0.0
    if prev_start and prev_end:
        prev_completed_orders = Order.query.filter(
            Order.created_at >= prev_start,
            Order.created_at < prev_end,
            Order.status == 'completed'
        ).all()
        if prev_completed_orders and hasattr(Order, 'ready_at'):
            prev_prep_times = [
                (o.ready_at - o.created_at).total_seconds()
                for o in prev_completed_orders
                if o.ready_at is not None
            ]
            if prev_prep_times:
                prev_avg_prep_mins = (sum(prev_prep_times) / len(prev_prep_times)) / 60

    # ---------------------------------------------------------
    # 6. Calculate Item Sales Distribution (Rank Item by Sales Count)
    # ---------------------------------------------------------
    item_sales = db.session.query(
        OrderItem.item_name,
        func.sum(OrderItem.quantity).label('quantity_sold')
    ).join(Order).filter(
        Order.created_at >= start_date,
        Order.status == 'completed'
    ).group_by(OrderItem.item_name).order_by(
        func.sum(OrderItem.quantity).desc()
    ).limit(5).all()
    item_sales_distribution = {
        item_name: int(quantity_sold or 0)
        for item_name, quantity_sold in item_sales
    }
    top_selling_items = get_top_selling_items(start_date, end_date)
  

    # ---------------------------------------------------------
    # 7. Calculate Category Sales Distribution
    # ---------------------------------------------------------
    category_sales_distribution = get_top_category(start_date, end_date)

    # ---------------------------------------------------------
    # 5. Extract Final Arrays and Top KPIs
    # ---------------------------------------------------------
    chart_labels = [b['label'] for b in buckets.values()]
    chart_revenue = [b['revenue'] for b in buckets.values()]
    chart_traffic = [b['traffic'] for b in buckets.values()]

    current_revenue = sum(chart_revenue)
    
    # Find the busiest time by searching the buckets dictionary for max traffic
    best_bucket = max(buckets.values(), key=lambda b: b['traffic'])
    highest_traffic_time = best_bucket['label'] if best_bucket['traffic'] > 0 else "--:--"

    kpi_data = {
        'revenue': f"${current_revenue:,.2f}",
        'revenue_trend': calculate_trend(current_revenue, prev_revenue),
        'meals': int(current_meals),
        'meals_trend': calculate_trend(current_meals, prev_meals),
        'prep': f"{avg_prep_mins:.1f} mins",
        'prep_trend': calculate_trend(avg_prep_mins, prev_avg_prep_mins), # Difficult to track historical prep reliably without logs
        'traffic': highest_traffic_time
    }
   
    return {
        'kpi': kpi_data,
        'chart_labels': chart_labels,
        'chart_revenue': chart_revenue,
        'chart_traffic': chart_traffic,
        'item_sales_distribution': top_selling_items,
        'category_sales_distribution': category_sales_distribution
        
    }

