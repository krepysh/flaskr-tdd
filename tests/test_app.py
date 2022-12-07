import pytest
from flask.testing import FlaskClient

from project.app import app, db
from pathlib import Path

TEST_DB = "test_db.sqlite3"


@pytest.fixture
def client():
    basedir = Path(__file__).resolve().parent.parent
    app.config["DATABASE"] = Path(basedir).joinpath(TEST_DB)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{app.config["DATABASE"]}'

    db.create_all()
    yield app.test_client()
    db.drop_all()


def login(client: FlaskClient):
    username = app.config["USER_NAME"]
    password = app.config["PASSWORD"]

    return client.post(
        "/login", data=dict(username=username, password=password), follow_redirects=True
    )


def logout(client: FlaskClient):
    return client.post("/logout", follow_redirects=True)


@pytest.fixture
def logged_in_client(client: FlaskClient) -> FlaskClient:
    login(client)
    return client


def test_index(client):
    response = client.get("/", content_type="html/text")
    assert response.status_code == 200


def test_login_logout(client):
    res = login(client)
    assert res.status_code == 200
    logout_result = logout(client)
    assert logout_result.status_code == 200


def test_db():
    db.create_all()
    assert Path("test_db.sqlite3").is_file()


def test_empty_db(client):
    response = client.get("/")
    assert b"No messages, yet. Add one." in response.data


def test_add_entry(logged_in_client):
    response = logged_in_client.post(
        "/add_entry", data=dict(title="ttitle", body="tbody"), follow_redirects=True
    )
    assert response.status_code == 200
    assert b"ttitle" in response.data
    assert b"tbody" in response.data


def test_delete_message(logged_in_client):
    test_add_entry(logged_in_client)
    response = logged_in_client.post("/delete/1", follow_redirects=True)

    assert response.json == {"result": 1, "message": "Post deleted"}
