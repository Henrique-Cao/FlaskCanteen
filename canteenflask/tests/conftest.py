from collections import Counter

import pytest
from sqlalchemy import URL, event, text

from app import create_app
from app.extensions import db
from app.models import Category, MenuItem, User


_selected_tests = pytest.StashKey[Counter[str]]()


def pytest_collection_finish(session):
    session.config.stash[_selected_tests] = Counter(item.nodeid for item in session.items)


@pytest.hookimpl(trylast=True)
def pytest_terminal_summary(terminalreporter):
    if terminalreporter.config.option.collectonly:
        return

    selected = terminalreporter.config.stash.get(_selected_tests, None)
    if selected is None:
        return

    remaining = selected.copy()
    counts = Counter()
    for outcome, groups in (
        ("failed", ("failed", "error")),
        ("skipped", ("skipped",)),
        ("xfailed", ("xfailed",)),
        ("xpassed", ("xpassed",)),
        ("passed", ("passed",)),
    ):
        for group in groups:
            for report in terminalreporter.stats.get(group, []):
                if remaining[report.nodeid] > 0:
                    remaining[report.nodeid] -= 1
                    counts[outcome] += 1

    collection_errors = sum(
        report.nodeid not in selected for report in terminalreporter.stats.get("error", [])
    )
    terminalreporter.write_sep(
        "=",
        f"Test results: {counts['passed']}/{selected.total()} passed; "
        f"{counts['failed']} failed; {counts['skipped']} skipped; "
        f"{counts['xfailed']} xfailed; {counts['xpassed']} xpassed; "
        f"{remaining.total()} not completed; {collection_errors} collection errors",
    )


@pytest.fixture
def app(tmp_path, monkeypatch):
    unsafe_url = URL.create("sqlite", database=str(tmp_path / "must-not-be-used.db"))
    monkeypatch.setenv("DATABASE_URL", unsafe_url.render_as_string())
    app = create_app("testing")
    assert app.config["TESTING"]
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"
    app.config.update(SECRET_KEY="test-only-secret", UPLOAD_FOLDER=str(tmp_path))

    with app.app_context():
        engine = db.engine

        @event.listens_for(engine, "connect")
        def enable_foreign_keys(connection, _record):
            connection.execute("PRAGMA foreign_keys=ON")

        db.session.execute(text("PRAGMA foreign_keys=ON"))

    yield app

    with app.app_context():
        db.session.remove()
        engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def menu_item(app):
    with app.app_context():
        category = Category(name="Meals", display_order=1)
        item = MenuItem(name="Rice", price=3.5, category=category)
        db.session.add(item)
        db.session.commit()
        return item.id


@pytest.fixture
def admin_user(app):
    with app.app_context():
        user = User(username="test-admin", email="admin@example.test", role="admin")
        user.set_password("test-password")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def admin_client(client, admin_user):
    response = client.post(
        "/api/auth/login", json={"username": "test-admin", "password": "test-password"}
    )
    assert response.status_code == 200
    return client
