# seed_data.py
import os
from datetime import datetime, timezone, timedelta
from app import create_app
from app.extensions import db
from app.models import MenuItem, Order, OrderItem

app = create_app()

def seed_database():
    print("⏳ Initializing database seeding...")
    
    # 1. Clear out any existing test data to prevent duplicate unique constraints
    print("🧹 Cleaning up old records...")
    db.session.query(OrderItem).delete()
    db.session.query(Order).delete()
    db.session.query(MenuItem).delete()
    db.session.commit()

    # 2. Define Sample Menu Items
    print("🍳 Inserting menu items...")
    menu_items_data = [
        # Mains
        {"name": "Chicken Rice", "description": "Tender poached chicken served with fragrant seasoned rice and chili sauce.", "price": 4.50, "category": "Mains"},
        {"name": "Laksa", "description": "Spicy noodle soup with a rich, creamy coconut curry broth, prawns, and fishcakes.", "price": 5.50, "category": "Mains"},
        {"name": "Mee Rebus", "description": "Yellow noodles in a thick, spicy sweet potato gravy, topped with a boiled egg.", "price": 4.00, "category": "Mains"},
        {"name": "Nasi Lemak", "description": "Fragrant coconut rice served with crispy ikan bilis, fried chicken, fried egg, and sambal.", "price": 5.00, "category": "Mains"},
        
        # Drinks
        {"name": "Kopi", "description": "Traditional Nanyang-style black coffee with condensed milk.", "price": 1.50, "category": "Drinks"},
        {"name": "Teh C", "description": "Traditional brewed tea with evaporated milk and sugar.", "price": 1.60, "category": "Drinks"},
        {"name": "Iced Milo", "description": "Chilled malty chocolate beverage topped with ice.", "price": 2.00, "category": "Drinks"},
        {"name": "Lime Juice", "description": "Refreshing and tart calamansi lime drink.", "price": 1.80, "category": "Drinks"}
    ]

    inserted_items = {}
    for item in menu_items_data:
        m_item = MenuItem(
            name=item["name"],
            description=item["description"],
            price=item["price"],
            category=item["category"],
            is_available=True
        )
        db.session.add(m_item)
        # Flush here lets SQLAlchemy assign IDs immediately without closing the transaction
        db.session.flush() 
        inserted_items[item["name"]] = m_item

    # 3. Create Sample Orders
    print("📦 Generating mock customer orders...")
    
    # Order 1: A pending breakfast order
    order_1 = Order(
        order_number="ORD-20260630-01",
        customer_name="Henry Tan",
        phone="91234567",
        status=Order.STATUS_PENDING,
        created_at=datetime.now(timezone.utc) - timedelta(minutes=15)
    )
    db.session.add(order_1)
    db.session.flush()

    # Link line items to Order 1
    item_1a = OrderItem(order_id=order_1.id, menu_item_id=inserted_items["Nasi Lemak"].id, quantity=1, unit_price=inserted_items["Nasi Lemak"].price)
    item_1b = OrderItem(order_id=order_1.id, menu_item_id=inserted_items["Kopi"].id, quantity=1, unit_price=inserted_items["Kopi"].price)
    db.session.add_all([item_1a, item_1b])
    order_1.total_price = item_1a.subtotal + item_1b.subtotal

    # Order 2: A ready order waiting for pickup
    order_2 = Order(
        order_number="ORD-20260630-02",
        customer_name="Siti Aminah",
        phone="87654321",
        status=Order.STATUS_READY,
        created_at=datetime.now(timezone.utc) - timedelta(minutes=45)
    )
    db.session.add(order_2)
    db.session.flush()

    # Link line items to Order 2
    item_2a = OrderItem(order_id=order_2.id, menu_item_id=inserted_items["Chicken Rice"].id, quantity=2, unit_price=inserted_items["Chicken Rice"].price)
    item_2b = OrderItem(order_id=order_2.id, menu_item_id=inserted_items["Iced Milo"].id, quantity=2, unit_price=inserted_items["Iced Milo"].price)
    db.session.add_all([item_2a, item_2b])
    order_2.total_price = item_2a.subtotal + item_2b.subtotal

    # Order 3: An older, archived collected order
    order_3 = Order(
        order_number="ORD-20260630-03",
        customer_name="David Lim",
        phone="98127346",
        status=Order.STATUS_COLLECTED,
        created_at=datetime.now(timezone.utc) - timedelta(hours=3)
    )
    db.session.add(order_3)
    db.session.flush()

    item_3a = OrderItem(order_id=order_3.id, menu_item_id=inserted_items["Laksa"].id, quantity=1, unit_price=inserted_items["Laksa"].price)
    item_3b = OrderItem(order_id=order_3.id, menu_item_id=inserted_items["Lime Juice"].id, quantity=1, unit_price=inserted_items["Lime Juice"].price)
    db.session.add_all([item_3a, item_3b])
    order_3.total_price = item_3a.subtotal + item_3b.subtotal

    # Final commit to store all entries into project.db
    db.session.commit()
    print("✅ Database successfully seeded with menu items and orders!")

if __name__ == "__main__":
    with app.app_context():
        seed_database()