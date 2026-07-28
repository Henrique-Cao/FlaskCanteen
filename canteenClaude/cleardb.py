# seed_data.py
import os
from datetime import datetime, timezone, timedelta
from app import create_app
from app.extensions import db
from app.models import MenuItem, Order, OrderItem, Category 

app = create_app()

def clear_database():
    print("⏳ Initializing database seeding...")
    
    # 1. Clear out any existing test data to prevent duplicate unique constraints
    print("🧹 Cleaning up old records...")
    db.session.query(OrderItem).delete()
    db.session.query(Order).delete()
    db.session.query(MenuItem).delete()
    db.session.query(Category).delete()  # Clear categories as well
    db.session.commit()
    print("✅ Database cleared successfully.")
if __name__ == "__main__":
    with app.app_context():
        clear_database()