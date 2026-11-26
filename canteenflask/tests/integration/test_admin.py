from io import BytesIO

from PIL import Image

from app.extensions import db
from app.models import Category, MenuItem, Order, User


def image_file():
    data = BytesIO()
    Image.new("RGB", (4, 4), "red").save(data, format="PNG")
    data.seek(0)
    return data


def test_admin_login_logout_and_authorization(client, app, admin_user):
    assert client.get("/admin/").status_code == 302
    response = client.post("/api/auth/login", json={"username": "test-admin", "password": "wrong"})
    assert response.status_code == 401
    assert client.get("/admin/").status_code == 302
    response = client.post("/api/auth/login", json={"username": "test-admin", "password": "test-password"})
    assert response.status_code == 200
    assert response.get_json()["user"]["role"] == "admin"
    assert client.get("/admin/").status_code == 200
    assert client.post("/api/auth/logout").get_json()["success"]
    assert client.get("/admin/").status_code == 302

    with app.app_context():
        user = User(username="non-admin", email="user@example.test", role="customer")
        user.set_password("test-password")
        db.session.add(user)
        db.session.commit()
    assert client.post("/api/auth/login", json={"username": "non-admin", "password": "test-password"}).status_code == 200
    assert client.get("/admin/").status_code == 403


def test_category_create_update_reorder_and_delete(admin_client, app):
    assert admin_client.post("/api/categories/add", json={"name": ""}).status_code == 400
    first = admin_client.post("/api/categories/add", json={"name": "Drinks"}).get_json()["category"]
    second = admin_client.post("/api/categories/add", json={"name": "Food"}).get_json()["category"]
    assert admin_client.post(f"/api/categories/update/{first['id']}", json={"name": "  Beverages  "}).status_code == 200
    assert admin_client.post(f"/api/categories/update/{first['id']}", json={"name": " "}).status_code == 400
    assert admin_client.post("/api/categories/reorder", json={"ordered_ids": [second["id"], first["id"]]}).status_code == 200
    categories = admin_client.get("/api/categories/").get_json()
    assert [(item["name"], item["display_order"]) for item in categories] == [("Food", 1), ("Beverages", 2)]
    assert admin_client.post(f"/api/categories/delete/{first['id']}").status_code == 200
    assert admin_client.post(f"/api/categories/delete/{first['id']}").status_code == 404
    with app.app_context():
        assert db.session.get(Category, first["id"]) is None


def test_menu_upload_update_visibility_and_delete(admin_client, app, menu_item, tmp_path):
    with app.app_context():
        category_id = db.session.get(MenuItem, menu_item).category_id
    response = admin_client.post("/api/menu/", data={
        "addName": "Noodles", "addCategory": str(category_id), "addPrice": "5.25",
        "addDescription": "Test dish", "image": (image_file(), "sample.png"),
    })
    assert response.status_code == 201
    item_id = response.get_json()["item_id"]
    with app.app_context():
        item = db.session.get(MenuItem, item_id)
        saved = tmp_path / item.image_filename
        assert saved.is_file()
        assert item.name == "Noodles"
    assert admin_client.get(f"/api/menu/{item_id}").get_json()["price"] == 5.25
    assert admin_client.post(f"/api/menu/toggle/{item_id}/false").get_json()["is_available"] is False
    response = admin_client.post(f"/api/menu/update/{item_id}", data={
        "editName": "Updated", "editCategory": str(category_id),
        "editPrice": "6.00", "editDescription": "Updated dish",
        "editImage": (image_file(), "replacement.png"),
    })
    assert response.status_code == 200
    assert admin_client.get(f"/api/menu/{item_id}").get_json()["name"] == "Updated"
    with app.app_context():
        replacement = tmp_path / db.session.get(MenuItem, item_id).image_filename
        assert replacement.is_file()
    assert admin_client.delete(f"/api/menu/{item_id}").status_code == 200
    assert not replacement.exists()
    assert admin_client.delete(f"/api/menu/{item_id}").status_code == 404
    with app.app_context():
        assert db.session.get(MenuItem, item_id) is None


def test_invalid_image_does_not_create_menu_item(admin_client, app, menu_item):
    with app.app_context():
        category_id = db.session.get(MenuItem, menu_item).category_id
    response = admin_client.post("/api/menu/", data={
        "addName": "Broken", "addCategory": str(category_id), "addPrice": "5",
        "image": (BytesIO(b"not an image"), "invalid.png"),
    })
    assert response.status_code == 302
    with app.app_context():
        assert db.session.query(MenuItem).filter_by(name="Broken").count() == 0


def test_order_status_actions(admin_client, app):
    with app.app_context():
        order = Order(order_number="ORD-0001", customer_name="Test", phone="555", total_price=3.5)
        cancelled_order = Order(order_number="ORD-0002", customer_name="Test", phone="555", total_price=3.5)
        db.session.add_all([order, cancelled_order])
        db.session.commit()
        order_id = order.id
        cancelled_id = cancelled_order.id
    assert admin_client.put(f"/api/order/{order_id}/status", json={"status": "invalid"}).status_code == 400
    assert admin_client.put("/api/order/99999/complete").status_code == 404
    assert admin_client.put(f"/api/order/{order_id}/status", json={"status": "ready"}).get_json()["status"] == "ready"
    with app.app_context():
        assert db.session.get(Order, order_id).ready_at is not None
    assert admin_client.put(f"/api/order/{order_id}/complete").get_json()["status"] == "completed"
    with app.app_context():
        assert db.session.get(Order, order_id).completed_at is not None
    assert admin_client.put(f"/api/order/{cancelled_id}/cancel").get_json()["status"] == "cancelled"
    with app.app_context():
        assert db.session.get(Order, cancelled_id).cancelled_at is not None
