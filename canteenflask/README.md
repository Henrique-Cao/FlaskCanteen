# Club33 Canteen Application

This directory contains the Flask application for the Canteen Order Rail project. It provides customer menu, cart, order placement and tracking pages, plus staff menu management, order management, and analytics.

For the repository overview and full documentation, start at the [project README](../README.md) and [documentation index](../docs/README.md).

## Run locally

Requires Python 3.10 or later. From this directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt -r requirements-dev.txt
python run.py
```

On macOS or Linux, replace the activation command with `source .venv/bin/activate`. Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

The default SQLite database is `instance/club33.db`; the app creates missing tables on startup. See [configuration and deployment](../docs/configuration-and-deployment.md) before using non-development settings.

## Tests

From this directory:

```bash
python -m pytest
```

Test configuration and focused commands are documented in the [Getting started guide](../docs/getting-started.md#run-tests). `seeddb.py` is destructive and must only be run against disposable development data.
