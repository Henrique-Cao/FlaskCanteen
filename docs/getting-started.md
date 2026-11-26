# Getting started

This guide is for developers setting up the Flask application locally.

## Prerequisites

- Python 3.10 or later
- pip

## Create an environment and install dependencies

Run these commands from the repository root in PowerShell:

```powershell
cd canteenClaude
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt -r requirements-dev.txt
```

If PowerShell prevents script activation, use the virtual environment's interpreter directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt
```

On macOS or Linux:

```bash
cd canteenClaude
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt -r requirements-dev.txt
```

## Start the development server

From `canteenClaude/`, run:

```bash
python run.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000). `run.py` creates the Flask app and, in development mode, compiles the Sass assets on startup. The application factory creates database tables if they do not already exist. The default SQLite file is `canteenClaude/instance/club33.db`.

The app reads optional settings from environment variables and a `.env` file. See [Configuration and deployment](configuration-and-deployment.md).

## Run tests

From `canteenClaude/`:

```bash
python -m pytest
```

Useful focused commands:

```bash
python -m pytest --collect-only
python -m pytest tests/unit
python -m pytest tests/integration
python -m pytest --cov=app --cov-report=term-missing
```

`pytest.ini` limits test discovery to `tests/`. The fixtures in `tests/conftest.py` use an in-memory SQLite database, a temporary upload folder, a test-only secret, and enabled SQLite foreign keys. Do not point tests at a real database or uploads directory.

## Sample data warning

`seeddb.py` is for disposable development data only. Running it deletes and recreates the tables in the database selected by the current configuration before populating sample data. Do not run it against a database containing data you need to keep or against a production database.
