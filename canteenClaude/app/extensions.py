"""
extensions.py
~~~~~~~~~~~~~
Extension instances — initialised without an app object to avoid
circular imports. The factory calls .init_app(app) for each.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
 

db = SQLAlchemy()
migrate = Migrate()
 