# Configuration and deployment

The application has development, production, testing, and default configuration classes in `canteenClaude/config.py`. The app factory selects a class using `FLASK_ENV` (default: `default`, which maps to development).

## Environment variables

| Variable | Behavior |
|---|---|
| `SECRET_KEY` | Flask session signing key. The code has a development fallback; set a unique, high-entropy value outside local development. |
| `DATABASE_URL` | SQLAlchemy database URL. If unset, the app uses `canteenClaude/instance/club33.db`. |
| `FLASK_ENV` | Selects the app config name: `development`, `production`, or `testing`. |

`python-dotenv` is installed and `config.py` calls `load_dotenv()`, so local settings can be placed in a `.env` file. Do not commit real secrets or production database credentials.

Example local development settings:

```dotenv
FLASK_ENV=development
SECRET_KEY=replace-with-a-random-local-secret
```

For PowerShell, environment variables can also be set for the current terminal:

```powershell
$env:FLASK_ENV = "development"
$env:SECRET_KEY = "replace-with-a-random-local-secret"
python run.py
```

## Database and migrations

`create_app()` calls SQLAlchemy `create_all()` at startup. This creates missing tables, but it does not migrate existing tables when models change. Flask-Migrate is initialized, but a checked-in migration workflow is not part of this source tree. Plan and test schema changes explicitly before upgrading a database with real data.

The test configuration always uses in-memory SQLite. Do not infer production database compatibility from SQLite tests alone; test any alternate database and its driver separately.

## Production readiness

The checked-in configuration is not a complete production deployment recipe:

- The Flask secret falls back to a known development value unless `SECRET_KEY` is configured.
- The production config disables Flask debug mode, but does not by itself provide a production WSGI server, TLS, backups, logging, or operational monitoring.
- Admin page routes enforce authentication, but JSON API write routes do not consistently enforce admin authorization.
- `seeddb.py` drops and recreates tables. Never run it against a live database.
- Uploaded images live under the application static directory; plan persistent storage and backups if deployments are ephemeral.

Before deploying, use a unique secret, configure a production database and reliable backups, add and verify API authorization, use a production WSGI server behind HTTPS, and test the deployment configuration without real customer data.
