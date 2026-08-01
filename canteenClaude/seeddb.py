import sys
from app import create_app, db
from app.models import Category, MenuItem

# Initialize Flask Application Context
app = create_app()

def seed_database():
    with app.app_context():
        print("--- Starting Database Seeding ---")
        
        # 1. Create database tables if they don't exist
        db.create_all()

        # 2. Initial Category Data
        categories_data = [
            {"name": "Mains", "position": 1},
            {"name": "Drinks", "position": 2},
            {"name": "Snacks", "position": 3},
        ]

        category_map = {}
        for cat_info in categories_data:
            cat = Category.query.filter_by(name=cat_info["name"]).first()
            if not cat:
                cat = Category(name=cat_info["name"],display_order=cat_info["position"])
                db.session.add(cat)
                db.session.flush()  # Flushes session to get cat.id immediately
                print(f"[+] Added Category: '{cat.name}' (ID: {cat.id})")
            else:
                print(f"[=] Category already exists: '{cat.name}' (ID: {cat.id})")
            category_map[cat.name] = cat.id

        db.session.commit()

        # 3. Initial Menu Item Data (Linked to categories + 1 Uncategorized item)
        items_data = [
            {
                "name": "Chicken Rice",
                "price": 4.50,
                "description": "Steamed chicken with fragrant rice and chili sauce.",
                "category_id": category_map.get("Mains"),
                "is_available": True
            },
            {
                "name": "Iced Lemon Tea",
                "price": 1.80,
                "description": "Refreshing iced tea with fresh lemon slice.",
                "category_id": category_map.get("Drinks"),
                "is_available": True
            },
            {
                "name": "Curry Puff",
                "price": 1.50,
                "description": "Crispy pastry filled with spiced potato and chicken.",
                "category_id": category_map.get("Snacks"),
                "is_available": True
            },
            {
                "name": "Bottled Mineral Water",
                "price": 1.00,
                "description": "500ml cold mineral water.",
                "category_id": None,  # Tests optional / uncategorized logic
                "is_available": True
            }
        ]

        for item_info in items_data:
            existing_item = MenuItem.query.filter_by(name=item_info["name"]).first()
            if not existing_item:
                new_item = MenuItem(
                    name=item_info["name"],
                    price=item_info["price"],
                    description=item_info["description"],
                    category_id=item_info["category_id"],
                    is_available=item_info["is_available"],
                    image_filename="placeholder.jpg"
                )
                db.session.add(new_item)
                cat_display = item_info["category_id"] if item_info["category_id"] else "None (Uncategorized)"
                print(f"[+] Added MenuItem: '{new_item.name}' -> Category ID: {cat_display}")
            else:
                print(f"[=] MenuItem already exists: '{existing_item.name}'")

        db.session.commit()
        print("--- Database Seeding Complete! ---")

if __name__ == "__main__":
    seed_database()