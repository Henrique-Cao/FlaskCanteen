# Club33 Canteen Flask App

This project is a Flask-based canteen ordering application for Club33.
It includes:

- a public menu experience for customers
- an admin area for managing categories and menu items
- order tracking with statuses such as pending, confirmed, ready, and collected

## Project structure

- app/ - application package containing models, routes, templates, and static assets
- config.py - configuration settings for development, testing, and production
- run.py - development entry point
- requirements.txt - Python dependencies

## Getting started

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the development server:
   ```bash
   python run.py
   ```

## Notes

The application uses Flask-SQLAlchemy with SQLite by default. The database file is created under the instance directory when the app starts.

## Backend tests

The backend tests use pytest. Python 3.13 was used to verify the setup. From
the project root in PowerShell, create or activate a virtual environment and
install both application and test dependencies:

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
python -m pip install -r requirements.txt -r requirements-dev.txt
```

If `env` already exists, activate it instead of creating it again. The existing
`requirements.txt` uses UTF-16 encoding; pip can read it directly. If activation
is blocked by PowerShell policy, run the commands using
`.\env\Scripts\python.exe` instead of `python`.

```powershell
python -m pytest --collect-only
python -m pytest tests\unit
python -m pytest tests\integration
python -m pytest
python -m pytest --cov=app --cov-report=term-missing
```

The test summary shows how many selected tests passed out of the total, along
with failures, skips, expected failures, unexpected passes, tests not completed,
and collection errors. For example, `39/39 passed` means all 39 selected tests
passed. A filtered run counts only the tests selected for that run.

Test discovery is restricted to `tests`; the root `test.py` is a data-generation
script, not part of the suite. Add focused tests in `tests\unit` for isolated
behavior or `tests\integration` for Flask requests and database behavior. Reuse
the fixtures in `tests\conftest.py`; tests must not use real customer data,
the normal database, or the real uploads directory.

Each test app uses a fresh in-memory SQLite database, an isolated temporary
uploads directory, and a test secret. SQLite foreign-key enforcement is enabled
in the test fixture, which may expose constraints not enforced by the normal
application configuration. If production uses a different database, add
integration tests for that database separately; SQLite does not prove that
database-specific queries will work elsewhere.

The initial coverage baseline was 77% of application statements, with no
minimum threshold enforced. Treat coverage as a guide to missing cases, not a
measure of correctness. Existing SQLAlchemy `Query.get()` deprecation warnings
are emitted by application code; they do not indicate test failures.

For CI, install the same requirements into an isolated Python environment and
run `python -m pytest --cov=app --cov-report=term-missing`. Fail the job on a
nonzero exit code; no server or production credentials are needed. A
platform-specific workflow can be added when a CI platform is chosen.

### Existing issues to triage

These are not fixed or treated as acceptable behavior by the test suite:

- **High priority: admin API authorization.** An anonymous
  `POST /api/categories/add` with a valid name creates a category (201).
  Other menu and order management endpoints also lack visible admin guards.
  Confirm which endpoints require admin access, then protect them and test
  anonymous, non-admin, and admin access.
- **High priority: alternate order creation.** `POST /api/order/create` imports
  `create_order_from_cart`, which is absent from `app.services.order_service`,
  causing an import error. Confirm whether this endpoint is still needed before
  fixing or removing it.
- **Medium priority: historical item names.** Order lines store a name snapshot,
  but confirmation pages use the current menu item name. Renaming a menu item
  can therefore change names displayed for old orders. Confirm the intended
  historical display behavior before changing it.
- **Cart routes:** `GET /cart/` references the missing `partials/_cart.html`
  template. The separate `/cart/checkout` route accepts only GET and currently
  returns no response. Confirm whether these routes are needed before fixing or
  removing them; the cart modal and order API are tested separately.
