# services/order_service.py
from datetime import datetime, timedelta
from sqlalchemy import or_
from app.models import Order

def get_filtered_orders_query(args):
    """
    Reads request parameters sent from the filter form 
    and returns a filtered, sorted SQLAlchemy query object.
    """
    # Start with all orders in the database
    query = Order.query

    # ------------------------------------------------------------------
    # 1. Universal Text Search (Order #, Customer Name, or Phone)
    # ------------------------------------------------------------------
    q = args.get('q', '').strip()
    if q:
        # Check if query matches order_number OR customer_name OR phone
        query = query.filter(
            or_(
                Order.order_number.ilike(f"%{q}%"),
                Order.customer_name.ilike(f"%{q}%"),
                Order.phone.ilike(f"%{q}%")
            )
        )

    # ------------------------------------------------------------------
    # 2. Status Filter (Checkboxes)
    # ------------------------------------------------------------------
    statuses = args.getlist('status')  # Gets list of all checked boxes
    if statuses:
        # Match any status inside the selected list
        query = query.filter(Order.status.in_(statuses))

    # ------------------------------------------------------------------
    # 3. Date Presets (Today, Yesterday, Last 7 Days, Custom Range)
    # ------------------------------------------------------------------
    date_preset = args.get('date_preset', '')
    start_date = args.get('start_date', '')
    end_date = args.get('end_date', '')
    today = datetime.now().date()

    if date_preset == 'today':
        query = query.filter(Order.created_at >= today)
    elif date_preset == 'yesterday':
        yesterday = today - timedelta(days=1)
        query = query.filter(Order.created_at >= yesterday, Order.created_at < today)
    elif date_preset == '7days':
        seven_days_ago = today - timedelta(days=7)
        query = query.filter(Order.created_at >= seven_days_ago)
    elif start_date or end_date:
        # Custom Date Range inputs
        if start_date:
            s_dt = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Order.created_at >= s_dt)
        if end_date:
            e_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query = query.filter(Order.created_at <= e_dt)

    # ------------------------------------------------------------------
    # 4. Price Range Filter
    # ------------------------------------------------------------------
    min_price = args.get('min_price', type=float)
    max_price = args.get('max_price', type=float)

    if min_price is not None:
        query = query.filter(Order.total_price >= min_price)
    if max_price is not None:
        query = query.filter(Order.total_price <= max_price)

    # Always return newest orders first
    return query.order_by(Order.created_at.desc())



def get_order_by_numeric_input(raw_digits: str):
    """
    Combines the visual 'ORD-' prefix with user-submitted digits 
    and queries the database.
    """
    if not raw_digits:
        return None

    # Strip any extra spaces or accidental 'ORD-' if copy-pasted
    clean_digits = raw_digits.strip().replace('ORD-', '').replace('ord-', '')

    # Construct full order key (e.g. "ORD-0450")
    full_order_id = f"ORD-{clean_digits}"

    return full_order_id