from datetime import datetime, timedelta

from sqlalchemy import func, desc
from app.models import db, Order, OrderItem, MenuItem, Category

def _build_range_config(date_range: str) -> dict:
    """Returns date bounds, empty time buckets, SQL format, and dynamic UI labels."""
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = today_start + timedelta(days=1)
    buckets = {}

    if date_range == '7d':
        start_date = today_start - timedelta(days=6)
        prev_start = start_date - timedelta(days=7)
        for i in range(7):
            day = start_date + timedelta(days=i)
            buckets[day.strftime('%Y-%m-%d')] = {
                'label': day.strftime('%a %d'),  # e.g., "Thu 19"
                'revenue': 0.0,
                'traffic': 0
            }
        return {
            'range': '7d',
            'start_date': start_date,
            'end_date': end_date,
            'prev_start': prev_start,
            'prev_end': start_date,
            'sql_format': '%Y-%m-%d',
            'buckets': buckets,
            'meta': {
                'revenue_title': 'Last 7 Days Revenue Trend',
                'traffic_title': 'Last 7 Days Traffic Trend',
                'peak_label': 'Busiest Day',
                'trend_suffix': 'vs prev 7 days'
            }
        }

    elif date_range == '30d':
        start_date = today_start - timedelta(days=29)
        prev_start = start_date - timedelta(days=30)
        for i in range(30):
            day = start_date + timedelta(days=i)
            buckets[day.strftime('%Y-%m-%d')] = {
                'label': day.strftime('%d %b'),  # e.g., "19 Nov"
                'revenue': 0.0,
                'traffic': 0
            }
        return {
            'range': '30d',
            'start_date': start_date,
            'end_date': end_date,
            'prev_start': prev_start,
            'prev_end': start_date,
            'sql_format': '%Y-%m-%d',
            'buckets': buckets,
            'meta': {
                'revenue_title': 'Last 30 Days Revenue Trend',
                'traffic_title': 'Last 30 Days Traffic Trend',
                'peak_label': 'Busiest Day',
                'trend_suffix': 'vs prev 30 days'
            }
        }

    # Default / Fallback: 'today' (also guards against invalid query params)
    prev_start = today_start - timedelta(days=1)
    for h in range(7, 19):  # Adjust to your canteen's operating hours (7 AM - 6 PM)
        label = f"{h if h <= 12 else h - 12} {'AM' if h < 12 else 'PM'}"
        buckets[f"{h:02d}"] = {'label': label, 'revenue': 0.0, 'traffic': 0}

    return {
        'range': 'today',
        'start_date': today_start,
        'end_date': end_date,
        'prev_start': prev_start,
        'prev_end': today_start,
        'sql_format': '%H',
        'buckets': buckets,
        'meta': {
            'revenue_title': "Today's Hourly Revenue Trend",
            'traffic_title': "Today's Hourly Traffic Trend",
            'peak_label': 'Highest Traffic Time',
            'trend_suffix': 'vs yesterday'
        }
    }


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


def get_period_data(start_date, end_date):
    filters = (
        Order.created_at >= start_date,
        Order.created_at < end_date,
        Order.status == 'completed'
    )
    revenue = db.session.query(func.sum(Order.total_price)).filter(*filters).scalar()
    meals = db.session.query(func.sum(OrderItem.quantity)).join(
        Order, OrderItem.order_id == Order.id
    ).filter(*filters).scalar()

    completion_field = next(
        (getattr(Order, name) for name in ('ready_at', 'prepared_at', 'completed_at')
         if hasattr(Order, name)),
        None
    )
    durations = []
    if completion_field is not None:
        timestamps = db.session.query(
            Order.created_at, completion_field
        ).filter(*filters, completion_field.isnot(None)).all()
        durations = [
            (ready - created).total_seconds() / 60
            for created, ready in timestamps
            if created is not None and ready >= created
        ]
    
    return {
        'total_revenue': float(revenue or 0),
        'total_meals': int(meals or 0),
        'average_prep_speed': round(sum(durations) / len(durations), 1) if durations else 0.0
    }

def get_kpis(start_date, end_date, prev_start, prev_end):
    # Total Revenue, Total Meals, Average Prep Speed,Highest Traffic Time (along with trends)
    current_data = get_period_data(start_date, end_date)
    previous_data = get_period_data(prev_start, prev_end)


    

    kpi_data = {
            'revenue': current_data['total_revenue'],
            'revenue_trend': calculate_trend(current_data['total_revenue'], previous_data['total_revenue']),
            'meals': current_data['total_meals'],
            'meals_trend': calculate_trend(current_data['total_meals'], previous_data['total_meals']),
            'prep': current_data['average_prep_speed'],
            'prep_trend': calculate_trend(current_data['average_prep_speed'], previous_data['average_prep_speed']), # Difficult to track historical prep reliably without logs
            'busiest_bucket': 'N/A'  # Placeholder, will be updated in get_dashboard_metrics2
            }
    return kpi_data
def get_dashboard_metrics2(date_range='today'):
    cfg = _build_range_config(date_range)
    
    # 1. Chart stats using cfg['sql_format'], cfg['start_date'], cfg['end_date'], cfg['buckets']
    buckets = cfg['buckets']
    sql_date_format = cfg['sql_format']
    start_date = cfg['start_date']
    end_date = cfg['end_date']
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
    
    # 2. KPI totals & previous period comparison using cfg['prev_start'], cfg['prev_end']
    kpi_data = get_kpis(cfg['start_date'], cfg['end_date'], cfg['prev_start'], cfg['prev_end'])

   
    # 3. Top 5 items & category sales using cfg['start_date'], cfg['end_date']

    top_items = get_top_selling_items(cfg['start_date'], cfg['end_date'], limit=5)
    top_categories = get_top_category(cfg['start_date'], cfg['end_date'], limit=5)



   
    chart_labels = [buckets[key]['label'] for key in buckets]
    chart_revenue = [buckets[key]['revenue'] for key in buckets]
    chart_traffic = [buckets[key]['traffic'] for key in buckets]

    # Determine the busiest traffic bucket
    busiest_bucket = max(
        ((key, buckets[key]['traffic']) for key in buckets),
        key=lambda x: x[1],
        default=(None, 0)
    )[0]
    kpi_data['traffic'] = buckets[busiest_bucket]['label'] if busiest_bucket else 'N/A'
    
    

    
    return {
        'range': cfg['range'],
        'meta': cfg['meta'],
        'kpi': kpi_data,
        'chart_labels': chart_labels,
        'chart_revenue': chart_revenue,
        'chart_traffic': chart_traffic,
        'top_items': top_items,
        'top_categories': top_categories,
    }