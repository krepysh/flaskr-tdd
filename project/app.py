import sqlite3

from flask import Flask, g

DATABASE = 'flaskr.sqlite3'

app = Flask(__name__)

app.config.from_object(__name__)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


def connect_db():
    connector = sqlite3.connect(app.config['DATABASE'])
    connector.row_factory = sqlite3.Row
    return connector


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', 'r') as f:
            cursor = db.cursor()
            cursor.executescript(f.read())
        db.commit()
    return


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


if __name__ == '__main__':
    app.run()
