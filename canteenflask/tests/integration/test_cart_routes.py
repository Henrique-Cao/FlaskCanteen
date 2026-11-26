from app.extensions import db
from app.models import MenuItem


def test_cart_quantity_modal_and_clear(client, menu_item):
    assert client.get("/cart/count").get_data(as_text=True) == ""
    empty = client.get("/cart/modal")
    assert empty.status_code == 200
    assert "Your cart is empty." in empty.get_data(as_text=True)

    response = client.post(f"/cart/update/{menu_item}", data={"delta": 2})
    assert response.status_code == 204
    assert response.headers["HX-Trigger"] == "cartUpdated"
    assert client.get("/cart/count").get_data(as_text=True) == "2"
    modal = client.get("/cart/modal").get_data(as_text=True)
    assert "Rice" in modal
    assert "$7.00" in modal
    assert "Total (2 items)" in modal

    assert client.post(f"/cart/update/{menu_item}", data={"delta": -1}).status_code == 204
    assert client.get("/cart/count").get_data(as_text=True) == "1"
    assert "$3.50" in client.get("/cart/modal").get_data(as_text=True)

    response = client.post("/cart/clear")
    assert response.status_code == 204
    assert response.headers["HX-Trigger"] == "cartUpdated"
    with client.session_transaction() as session:
        assert "cart" not in session
    assert client.get("/cart/count").get_data(as_text=True) == ""
    assert "Your cart is empty." in client.get("/cart/modal").get_data(as_text=True)


def test_cart_removes_zero_quantity_and_rejects_unknown_item(client, menu_item):
    assert client.post(f"/cart/update/{menu_item}").status_code == 204
    assert client.post(f"/cart/update/{menu_item}", data={"delta": -1}).status_code == 204
    with client.session_transaction() as session:
        assert str(menu_item) not in session["cart"]
    assert client.post("/cart/update/99999", data={"delta": 1}).status_code == 404
    assert client.get("/cart/count").get_data(as_text=True) == ""


def test_cart_modal_uses_current_prices_and_ignores_missing_items(client, app, menu_item):
    with client.session_transaction() as session:
        session["cart"] = {str(menu_item): 2, "99999": 3}
    with app.app_context():
        db.session.get(MenuItem, menu_item).price = 4.25
        db.session.commit()
    modal = client.get("/cart/modal")
    assert modal.status_code == 200
    assert "Rice" in modal.get_data(as_text=True)
    assert "$8.50" in modal.get_data(as_text=True)
    assert "Total (2 items)" in modal.get_data(as_text=True)

