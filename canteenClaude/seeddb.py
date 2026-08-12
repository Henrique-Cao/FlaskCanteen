import sys
from app import create_app, db
from app.models import Category, MenuItem, Order, OrderItem
from datetime import datetime, timedelta
# Initialize Flask Application Context
app = create_app()

def seed_database():
    with app.app_context():
        # 1. Create all tables
        db.create_all()

        # 2. Seed Categories
        if Category.query.first() is None:
            categories = [
                Category(name="Breakfast", display_order=1),
                Category(name="Lunch", display_order=2),
                Category(name="Drinks", display_order=3),
            ]
            db.session.bulk_save_objects(categories)
            db.session.commit()

        # 3. Seed Menu Items
        menu_items = [
            MenuItem(name="Pancakes", description="Fluffy pancakes with syrup", price=5.99, category_id=1),
            MenuItem(name="Burger", description="Juicy beef burger with cheese", price=8.99, category_id=2),
            MenuItem(name="Coffee", description="Freshly brewed coffee", price=2.99, category_id=3),
        ]
        # 4. Seed Orders and OrderItems (if needed)
        orders = [
            Order(order_number="ORD-0001", customer_name="Alice", phone="12345678", status=Order.STATUS_PENDING, total_price=11.98,created_at=datetime.now()),
            Order(order_number="ORD-0002", customer_name="Bob", phone="87654321", status=Order.STATUS_CONFIRMED, total_price=8.99,created_at=datetime.strptime("2026-08-11 09:00:00", "%Y-%m-%d %H:%M:%S")),
        ]
        # add order with status = ready and set ready_at to a specific time
        orders.append(Order(order_number="ORD-0003", customer_name="Charlie", phone="55555555", status=Order.STATUS_READY, total_price=2.99,created_at=datetime.strptime("2026-08-12 00:01:00", "%Y-%m-%d %H:%M:%S"),ready_at=datetime.strptime("2026-08-12 00:10:00", "%Y-%m-%d %H:%M:%S")))
        orders.append(Order(order_number="ORD-0004", customer_name="David", phone="44444444", status=Order.STATUS_COLLECTED, total_price=8.99,created_at=datetime.strptime("2026-08-12 00:02:00", "%Y-%m-%d %H:%M:%S"),ready_at=datetime.strptime("2026-08-12 00:09:00", "%Y-%m-%d %H:%M:%S")))
        


        db.session.bulk_save_objects(orders)
        db.session.commit()

        order_items = [
            OrderItem(order_id=1, menu_item_id=1, quantity=2, unit_price=5.99),
            OrderItem(order_id=2, menu_item_id=2, quantity=1, unit_price=8.99),
            OrderItem(order_id=1, menu_item_id=3, quantity=1, unit_price=2.99),
            OrderItem(order_id=2, menu_item_id=3, quantity=2, unit_price=2.99),
        ]
        db.session.bulk_save_objects(order_items)
        db.session.commit()



        db.session.bulk_save_objects(menu_items)
        db.session.commit()

        print("Database seeded successfully.")

if __name__ == "__main__":
    seed_database()