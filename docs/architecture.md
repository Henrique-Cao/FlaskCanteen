# Architecture

The project is a server-rendered Flask web application with a small JSON API used by interactive customer and staff pages. The application package lives in `canteenClaude/app/`; `canteenClaude/run.py` is the local development entry point.

## Request flow

1. `app.create_app()` creates the Flask application, loads a configuration, initializes SQLAlchemy, Flask-Migrate, and Flask-Login, creates missing tables, and registers blueprints.
2. Page routes render Jinja templates from `app/templates/`.
3. Interactive pages use JavaScript and JSON endpoints under `/api/`; cart actions are also available through `/cart/`.
4. Services in `app/services/` contain shared cart, order-filtering, and dashboard aggregation logic.
5. SQLAlchemy models in `app/models.py` persist categories, menu items, orders, order lines, and users.

## Application map

| Location | Responsibility |
|---|---|
| `app/__init__.py` | App factory, extension setup, login loader, and blueprint registration |
| `app/extensions.py` | Shared SQLAlchemy and migration extension objects |
| `app/models.py` | Database models and password hashing helpers |
| `app/main/` | Home, menu, confirmation, and tracking pages |
| `app/admin/` | Staff dashboard, menu, order, and history pages |
| `app/api/` | Authentication, menu, category, cart, order, and analytics endpoints |
| `app/cart/`, `app/order_confirmation/` | Cart fragments/actions and order confirmation/tracking routes |
| `app/services/` | Cart operations, order filtering, and dashboard calculations |
| `app/templates/` | Jinja page templates, modals, and partials |
| `app/static/` | JavaScript, CSS/SCSS, images, and uploaded menu images |
| `config.py` | Development, production, and testing configurations |
| `tests/` | Unit and Flask integration tests |

## Data model

- **Category** has a unique name and a display order. A category can contain many menu items.
- **MenuItem** has a name, description, price, optional category, image filename, and availability flag.
- **Order** has a unique order number, customer details, a total, timestamps, and a status.
- **OrderItem** links an order to a menu item and stores the quantity, item-name snapshot, and unit-price snapshot recorded at order time.
- **User** stores a unique username and email, a password hash, and a role.

The persisted order statuses are `pending`, `confirmed`, `ready`, `completed`, and `cancelled`. Order timestamps use a fixed UTC+08:00 timezone in the model and order-related operations. Orders and order lines are stored in the database; a customer's current cart is held in the Flask session.

## Persistence and files

SQLite is the default database, stored at `canteenClaude/instance/club33.db`. Set `DATABASE_URL` to use another SQLAlchemy-supported database URL. `create_app()` calls `db.create_all()` during startup; this creates missing tables but is not a versioned schema migration strategy.

Menu image uploads are written to `app/static/uploads/` using generated filenames. Tests override this path with a temporary directory.

## Authentication boundaries

The `/admin/` page blueprint checks that a user is signed in and has the admin role. Authentication is provided by the JSON login route under `/api/auth/`. The JSON API does not consistently enforce equivalent admin checks on write operations. Do not expose this application to an untrusted network until API authorization has been reviewed and enforced.

## Implementation caveats

- The application has more than one order/analytics implementation; the API and dashboard page do not share every calculation.
- `POST /api/order/create` refers to a service function that is not present; use `POST /api/order/` for the working session-cart order flow.
- The legacy `GET /cart/` view references a template that is not present, and `GET /cart/checkout` is unfinished. The cart modal and JSON cart endpoints are the implemented paths.
- Menu items have an availability flag and the staff page can update it, but the current customer menu templates do not filter on that flag.
- Order lines store item-name and price snapshots, but some page/API serializers read the current menu-item name. Historical display names can therefore differ after a menu rename.
- `run.py` compiles Sass output to `app/static/css/`, while active base templates link to `app/static/scss/main.css`. Verify the served stylesheet when changing Sass build behavior.
