import os
import sqlite3
from sqlite3 import Connection
from typing import NamedTuple

from flask import Flask, g, render_template, session, request, flash, redirect, url_for, abort

DATABASE = "flaskr.sqlite3"
USER_NAME = "admin"
PASSWORD = "admin"
SECRET_KEY = os.environ.get("SECRET_KEY")

app = Flask(__name__)

app.config.from_object(__name__)


@app.route("/")
def index():
    db = get_db()
    cur = db.execute("select * from entries order by id desc")
    entries = cur.fetchall()
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


def extract_entry(form: dict) -> Entry:
    title = form["title"]
    body = form["body"]
    return Entry(title=title, body=body)


@app.route("/add_entry", methods=["POST"])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    entry = extract_entry(request.form)
    db = get_db()
    query = "INSERT into entries (title, body) VALUES (?, ?);"
    cur = db.execute(query, entry)
    db.commit()
    flash(f"Inserted {cur.rowcount} rows.")
    return redirect(url_for("index"))


def connect_db() -> Connection:
    connector = sqlite3.connect(app.config["DATABASE"])
    connector.row_factory = sqlite3.Row
    return connector


def get_db() -> Connection:
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource("schema.sql", "r") as f:
            cursor = db.cursor()
            cursor.executescript(f.read())
        db.commit()
    return


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()


if __name__ == "__main__":
    app.run()
