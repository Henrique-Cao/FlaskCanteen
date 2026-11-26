# Canteen Order Rail

A Flask web application for canteen customers and staff. Customers can browse a menu, build a session-based cart, place orders, and look up order status. Staff can manage menu items and categories, review orders, and view sales analytics.

The application source and tests are in [`canteenClaude/`](canteenClaude/). This guide is for people running, operating, or contributing to the project.

## What it includes

- Customer-facing menu, cart, order placement, confirmation, and tracking pages.
- Staff dashboard, menu and category management, order management, and order history.
- JSON endpoints for menu, categories, cart, orders, and analytics.
- Flask-SQLAlchemy models backed by SQLite by default.
- A pytest suite covering service behavior and Flask routes.

## Run locally

### Requirements

- Python 3.10 or later
- pip

### Install and start

From the repository root:

```powershell
cd canteenClaude
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt -r requirements-dev.txt
python run.py
```

On macOS or Linux, activate the environment with:

```bash
cd canteenClaude
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt -r requirements-dev.txt
python run.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000). On first startup, the app creates its database tables. By default, the SQLite database is stored at `canteenClaude/instance/club33.db`.

For environment variables, test commands, and setup details, see the [Getting Started guide](docs/getting-started.md).

## Use the application

- **Customers:** browse the menu, add items to the cart, place an order, and use the order number or phone number to look up an order.
- **Staff:** sign in, then use the admin pages to manage the menu, categories, orders, and analytics.

See the [Customer and staff guide](docs/user-guide.md) for workflows and the [API reference](docs/api-reference.md) for routes and request formats.

## Documentation

| Guide | What it covers |
|---|---|
| [Documentation index](docs/README.md) | All project guides |
| [Getting started](docs/getting-started.md) | Installation, local run, and tests |
| [User guide](docs/user-guide.md) | Customer and staff workflows |
| [Menu management](docs/MenuManagement.md) | Editing menu items and categories |
| [Architecture](docs/architecture.md) | Application structure, data model, and request flow |
| [Configuration and deployment](docs/configuration-and-deployment.md) | Environment settings and operational cautions |
| [API reference](docs/api-reference.md) | Current page routes and JSON endpoints |
| [Contributing](CONTRIBUTING.md) | Contribution expectations and test workflow |

## Tests

Run the backend test suite from `canteenClaude/`:

```powershell
python -m pytest
```

The tests use isolated in-memory SQLite databases and temporary upload directories. See [Getting started](docs/getting-started.md#run-tests) for targeted test and coverage commands.

## Project status and safety

This repository is an application codebase, not a hosted service. Before making it available beyond a trusted development environment, configure a strong `SECRET_KEY`, review the admin API access controls, and follow the deployment cautions in [Configuration and deployment](docs/configuration-and-deployment.md).

The project is provided under the [MIT License](LICENSE).
