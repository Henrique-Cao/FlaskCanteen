import os
import subprocess
import sys

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from app import create_app
from app.extensions import db
from app.models import Category, MenuItem


def test_testing_app_ignores_database_url(app, tmp_path):
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"
    assert app.config["UPLOAD_FOLDER"] == str(tmp_path)
    with app.app_context():
        assert db.session.execute(text("PRAGMA foreign_keys")).scalar_one() == 1
    assert not (tmp_path / "must-not-be-used.db").exists()


def test_testing_app_ignores_database_url_before_import(app, tmp_path):
    subprocess.run(
        [
            sys.executable, "-c",
            "from app import create_app; "
            "app = create_app('testing'); "
            "assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'",
        ],
        env=os.environ.copy(),
        check=True,
    )
    assert not (tmp_path / "must-not-be-used.db").exists()


def test_committed_data_is_not_shared_between_test_apps(app):
    with app.app_context():
        db.session.add(Category(name="Only in first app"))
        db.session.commit()

    other = create_app("testing")
    with other.app_context():
        assert db.session.query(Category).count() == 0
        db.session.remove()
        db.engine.dispose()

    with app.app_context():
        assert db.session.query(Category).count() == 1


def test_foreign_keys_reject_invalid_menu_category(app):
    with app.app_context():
        db.session.add(MenuItem(name="Invalid", price=1, category_id=99999))
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()
        assert db.session.query(MenuItem).count() == 0
