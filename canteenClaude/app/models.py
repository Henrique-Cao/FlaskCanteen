"""
app/models.py
~~~~~~~~~~~~~
Database models for Club33.

Tables
------
MenuItem  — items auntie sells
Order     — a customer order (name, phone, status)
OrderItem — line items linking an Order to MenuItems
"""
from datetime import datetime, timezone
from app.extensions import db

class Category(db.Model):
    __tablename__ = "categories"

    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)

    items = db.relationship("MenuItem", backref="category", lazy=True)
    def __repr__(self):
        return f"<Category {self.name!r}>"
class MenuItem(db.Model):
    __tablename__ = "menu_items"

    id               = db.Column(db.Integer, primary_key=True)
    name             = db.Column(db.String(100), nullable=False)
    description      = db.Column(db.String(255), default="")
    price            = db.Column(db.Float,       nullable=False)
    category_id      = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    image_filename   = db.Column(db.String(120),  default="placeholder.jpg")
    is_available     = db.Column(db.Boolean,      default=True, nullable=False)

    # Relationship back to order lines
    order_items = db.relationship("OrderItem", back_populates="menu_item")

    def __repr__(self):
        return f"<MenuItem {self.name!r} ${self.price:.2f}>"


class Order(db.Model):
    __tablename__ = "orders"

    # Order status constants — use these instead of bare strings
    STATUS_PENDING   = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_READY     = "ready"
    STATUS_COLLECTED = "collected"

    id             = db.Column(db.Integer,    primary_key=True)
    order_number   = db.Column(db.String(16), unique=True, nullable=False, index=True)
    customer_name  = db.Column(db.String(100), nullable=False)
    phone          = db.Column(db.String(20),  nullable=False)
    status         = db.Column(db.String(20),  default=STATUS_PENDING, nullable=False)
    total_price    = db.Column(db.Float,       nullable=False, default=0.0)
    created_at     = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship to line items
    items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order {self.order_number!r} [{self.status}]>"


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id           = db.Column(db.Integer, primary_key=True)
    order_id     = db.Column(db.Integer, db.ForeignKey("orders.id"),      nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey("menu_items.id"),  nullable=False)
    quantity     = db.Column(db.Integer, nullable=False, default=1)
    unit_price   = db.Column(db.Float,   nullable=False)  # snapshot price at time of order

    order     = db.relationship("Order",    back_populates="items")
    menu_item = db.relationship("MenuItem", back_populates="order_items")

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def __repr__(self):
        return f"<OrderItem {self.menu_item_id} x{self.quantity}>"
