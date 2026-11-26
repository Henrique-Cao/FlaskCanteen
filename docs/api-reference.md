# HTTP and JSON API reference

This reference describes routes registered by the current Flask application. The app is typically served at `http://127.0.0.1:5000` in development.

## Page routes

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/` | Customer home page |
| `GET` | `/menu` | Customer menu |
| `GET` | `/confirmation/<order_number>` | Order confirmation |
| `GET`, `POST` | `/track_order` | Order lookup form and redirect |
| `GET` | `/order-confirmation/track?order_number=...` | Find an order using its number or phone |
| `GET` | `/order-confirmation/<order_number>` | Confirmation and current order status |
| `GET` | `/admin/` | Staff dashboard |
| `GET` | `/admin/manage-menu` | Menu and category management |
| `GET` | `/admin/orders` | Order management |
| `GET` | `/admin/history` | Completed order history |
| `GET` | `/admin/analytics/content` | Dashboard analytics fragment |

Admin page routes are protected by the admin blueprint's authentication and role checks.

## Authentication

### `POST /api/auth/login`

Accepts JSON:

```json
{
  "username": "staff-user",
  "password": "replace-with-your-password"
}
```

Successful requests establish a Flask-Login session and return the user details and redirect URL. Invalid credentials return `401`.

### `POST` or `GET /api/auth/logout`

Ends the current login session.

## Menu endpoints

| Method | Path | Request | Purpose |
|---|---|---|---|
| `GET` | `/api/menu/` | — | List menu items (`id`, `name`, `price`, `is_available`) |
| `GET` | `/api/menu/<item_id>` | — | Read one item's fields and category |
| `POST` | `/api/menu/` | Multipart fields `addName`, `addCategory`, `addPrice`, `addDescription`, optional `image` | Create an item |
| `POST` | `/api/menu/update/<item_id>` | Multipart fields `editName`, `editCategory`, `editPrice`, `editDescription`, optional `editImage` | Update an item |
| `DELETE` | `/api/menu/<item_id>` | — | Delete an item |
| `POST` | `/api/menu/toggle/<item_id>/<checked>` | `checked` is `true` or `false` | Change item availability |

## Category endpoints

| Method | Path | Request | Purpose |
|---|---|---|---|
| `GET` | `/api/categories/` | — | List categories by display order |
| `POST` | `/api/categories/add` | JSON: `{"name": "Drinks"}` | Create a category |
| `POST` | `/api/categories/update/<category_id>` | JSON: `{"name": "Hot drinks"}` | Rename a category |
| `POST` | `/api/categories/delete/<category_id>` | — | Delete a category |
| `POST` | `/api/categories/reorder` | JSON: `{"ordered_ids": [3, 1, 2]}` | Set category display order |

## Cart endpoints

The JSON cart is stored in the user's Flask session.

| Method | Path | Request | Purpose |
|---|---|---|---|
| `POST` | `/api/cart/add_to_cart` | Form field `item_id` | Add one item |
| `GET` | `/api/cart/get_cart` | — | Return item details, total price, and item count |
| `POST` | `/api/cart/update_quantity` | JSON: `{"item_id": "12", "quantity": 2}` | Set quantity; zero or less removes the item |
| `POST` | `/api/cart/clear` | — | Clear the session cart |

The HTML cart modal also uses `/cart/modal`, `/cart/count`, `/cart/update/<item_id>`, and `/cart/clear`. The older `/cart/` and `/cart/checkout` views are incomplete; see [Architecture](architecture.md).

## Order endpoints

| Method | Path | Request | Purpose |
|---|---|---|---|
| `POST` | `/api/order/` | JSON with `customer_name` and `customer_phone`; a non-empty cart must already be in the session | Create an order and clear the cart after success |
| `GET` | `/api/order/` | — | List orders, newest first |
| `GET` | `/api/order/active` | — | Currently returns the same order list as `/api/order/` |
| `GET` | `/api/order/<order_number>` | — | Read an order and its line items |
| `PUT` | `/api/order/<order_id>/status` | JSON: `{"status": "ready"}` | Set status to `pending`, `confirmed`, `ready`, or `completed` |
| `PUT` | `/api/order/<order_id>/complete` | — | Mark an order completed |
| `PUT` | `/api/order/<order_id>/cancel` | — | Mark an order cancelled |

For order creation, `customer_phone` may be omitted only when `verified_phone` is already present in the session. A successful response includes the order number indirectly through its `redirect_url`. Empty carts or missing customer details return `400`; unknown menu items return `404`.

`POST /api/order/create` is a legacy route that calls a service function not defined in the current code. Use `POST /api/order/` instead.

## Analytics

### `GET /api/analytics/?range=<period>`

`range` accepts `today`, `7d`, or `30d`; the default is `today`. The response contains `kpis`, `rush_hours`, `top_dishes`, and `categories` data for the staff dashboard.

The separate dashboard page uses `/admin/analytics/content?range=<period>` and returns an HTML fragment rather than JSON.

## Access-control note

Although admin pages require an authenticated admin user, JSON API write operations do not consistently apply the same authorization checks. Do not expose write endpoints to untrusted users or networks until this is addressed. This reference documents behavior; it is not a security guarantee.
