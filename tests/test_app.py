from project.app import app


def test_app():
    client = app.test_client()

    response = client.get('/', content_type='html/text')

    assert response.status_code == 200
    assert response.data == b'Hello World!'
