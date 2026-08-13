import sys
import os
import random
from pathlib import Path
from app import create_app, db
from app.models import Category, MenuItem, Order, OrderItem
from datetime import datetime, timedelta

# Initialize Flask Application Context
project_root = Path(__file__).resolve().parent
os.chdir(project_root)
(project_root / "instance").mkdir(parents=True, exist_ok=True)
app = create_app()


today = datetime.now()

# Number of orders to seed for yesterday and today respectively.
NUM_ORDERS_YESTERDAY = 200
NUM_ORDERS_TODAY = 250


def delete_database():
    """Delete all tables and data from the current database."""
    with app.app_context():
        db.drop_all()
        db.session.remove()
        print("Database deleted successfully.")


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
                Category(name="Desserts", display_order=4),
            ]
            db.session.bulk_save_objects(categories)
            db.session.commit()

        # 3. Seed Menu Items
        menu_items = [
            MenuItem(name="Pancakes", description="Fluffy pancakes with syrup", price=5.00, category_id=1),
            MenuItem(name="Sandwich", description="Ham and cheese sandwich", price=6.00, category_id=2),
            MenuItem(name="Burger", description="Juicy beef burger with cheese", price=8.00, category_id=2),
            MenuItem(name="Coffee", description="Freshly brewed coffee", price=2.00, category_id=3),
            MenuItem(name="Ice Cream", description="Vanilla ice cream scoop", price=3.00, category_id=4),
        ]

        # Save menu items before creating order items so their IDs are available.
        if MenuItem.query.first() is None:
            db.session.bulk_save_objects(menu_items)
            db.session.commit()

        # 4. Seed completed orders with pronounced breakfast, lunch, and dinner peaks.
        if Order.query.first() is None:
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            menu_items = MenuItem.query.all()
            rng = random.Random(42)

            # Most orders cluster around meal periods, with a small amount of
            # background traffic, so charts have visible highs and lows.
            orders = []
            order_number = 1
            # Seed a realistic traffic pattern for each day, using the configured
            # order counts while keeping most orders in the meal-period peaks.
            for day_offset, order_count in (
                (1, NUM_ORDERS_YESTERDAY),
                (0, NUM_ORDERS_TODAY),
            ):
                breakfast_count = round(order_count * 45 / 200)
                lunch_count = round(order_count * 105 / 200)
                dinner_count = round(order_count * 35 / 200)
                background_count = order_count - breakfast_count - lunch_count - dinner_count
                order_minutes = (
                    [rng.randint(7 * 60, 9 * 60 + 30) for _ in range(breakfast_count)]
                    + [rng.randint(11 * 60, 14 * 60 + 30) for _ in range(lunch_count)]
                    + [rng.randint(17 * 60, 19 * 60 + 30) for _ in range(dinner_count)]
                    + [rng.randint(9 * 60 + 30, 17 * 60) for _ in range(background_count)]
                )
                order_minutes.sort()

                day_start = today_start - timedelta(days=day_offset)
                for minutes_after_midnight in order_minutes:
                    created_at = day_start + timedelta(minutes=minutes_after_midnight)
                    # Lunch rushes take longer, while quieter periods are faster.
                    ready_delay = rng.randint(8, 24) if 11 * 60 <= minutes_after_midnight <= 14 * 60 + 30 else rng.randint(2, 12)
                    ready_at = created_at + timedelta(minutes=ready_delay)
                    orders.append(
                        Order(
                            order_number=f"ORD-{order_number:04d}",
                            customer_name=f"Customer {order_number}",
                            phone=f"{90000000 + order_number}",
                            status=Order.STATUS_COLLECTED,
                            total_price=0.00,
                            created_at=created_at,
                            ready_at=ready_at,
                        )
                    )
                    order_number += 1

            db.session.add_all(orders)
            db.session.commit()

            for index, order in enumerate(orders, start=1):
                selected_items = menu_items[(index - 1) % len(menu_items):] + menu_items[:(index - 1) % len(menu_items)]
                basket_size = rng.choices([1, 2, 3, 4, 5], weights=[12, 28, 35, 18, 7])[0]
                chosen_items = selected_items[: min(basket_size, len(menu_items))]
                item_total = 0.0

                for offset, menu_item in enumerate(chosen_items):
                    quantity = rng.choices([1, 2, 3, 4], weights=[55, 27, 13, 5])[0]
                    line_total = menu_item.price * quantity
                    item_total += line_total
                    db.session.add(
                        OrderItem(
                            order_id=order.id,
                            menu_item_id=menu_item.id,
                            item_name=menu_item.name,
                            quantity=quantity,
                            unit_price=menu_item.price,
                        )
                    )

                order.total_price = round(item_total, 2)

            db.session.commit()

        print("Database seeded successfully.")

if __name__ == "__main__":
    delete_database()
    seed_database()