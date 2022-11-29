from project.app import app, init_db
from pathlib import Path

def test_app():
    client = app.test_client()

    response = client.get('/', content_type='html/text')

    assert response.status_code == 200
    assert response.data == b'Hello World!'


def test_db():
    init_db()
    assert Path('flaskr.sqlite3').is_file()
