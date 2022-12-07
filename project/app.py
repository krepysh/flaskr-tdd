import os
from pathlib import Path
from typing import NamedTuple
from flask_sqlalchemy import SQLAlchemy
from flask import (
    Flask,
    g,
    render_template,
    session,
    request,
    flash,
    redirect,
    url_for,
    abort,
    jsonify,
)


basedir = Path(__file__).resolve().parent

DATABASE = "flaskr.sqlite3"
USER_NAME = "admin"
PASSWORD = "admin"
SECRET_KEY = os.environ.get("SECRET_KEY")
SQLALCHEMY_DATABASE_URI = f"sqlite:///{Path(basedir).joinpath(DATABASE)}"
SQLALCHEMY_TRACK_MODIFICATIONS = False

app = Flask(__name__)

app.config.from_object(__name__)
db = SQLAlchemy(app)

from project import models  # noqa: E402


@app.route("/")
def index():
    entries = db.session.query(models.Post)
    return render_template("index.html", entries=entries)


def validate_user(username, password) -> bool:
    return username == app.config["USER_NAME"] and password == app.config["PASSWORD"]


def user_login():
    session["logged_in"] = True


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        if validate_user(request.form["username"], request.form["password"]):
            user_login()
            return redirect(url_for("index"))
        error = "User not found."
        flash(error)
    return render_template("login.html")


@app.route("/logout", methods=["POST", "GET"])
def logout():
    session.pop("logged_in", None)
    flash("You've logged out.")
    return redirect(url_for("index"))


class Entry(NamedTuple):
    title: str
    body: str


def extract_entry(form: dict) -> models.Post:
    title = form["title"]
    body = form["body"]
    return models.Post(title=title, body=body)


@app.route("/add_entry", methods=["POST"])
def add_entry():
    if not session.get("logged_in"):
        abort(401)
    post = extract_entry(request.form)
    db.session.add(post)
    db.session.commit()
    flash(f"Inserted {1} rows.")
    return redirect(url_for("index"))


@app.route("/delete/<message_id>", methods=["GET", "POST"])
def delete_message(message_id):
    try:
        db.session.query(models.Post).filter_by(id=message_id).delete()
        db.session.commit()
        result = {"result": 1, "message": "Post deleted"}
    except Exception as e:
        result = {"result": 0, "message": str(e)}
    return jsonify(result)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()


if __name__ == "__main__":
    app.run()
