import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.before_app_request
def load_logged_in_user():
    try:
        user_id = session["user_id"]
        g.user = get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        # if user_id is None:
        #     g.user = None
        # else:
        #     g.user = get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
    except KeyError:
        g.user = None


@bp.get("/register")
def register_get():
    return render_template("auth/register.html")


@bp.post('/register')
def register_post():
    username = request.form['username']
    password = request.form['password']
    db = get_db()
    error = None
    if not username:
        error = "Username is required"
    elif not password:
        error = "Password is required"

    if error is None:
        try:
            db.execute("INSERT INTO user (username, password) VALUES (?, ?)",
                       (username, generate_password_hash(password))
                       )
            db.commit()
        except db.IntegrityError:
            error = f"Integrity error. User {username} is already registered."
        else:
            return redirect(url_for("auth.login_get"))
    flash(error)
    return render_template("auth/register.html")


@bp.get("/login")
def login_get():
    return render_template("auth/login.html")


@bp.post("/login")
def login_post():
    username = request.form["username"]
    password = request.form["password"]
    db = get_db()
    error = None
    user = db.execute("SELECT * FROM user WHERE username = ?", (username,)).fetchone()

    if user is None:
        error = "No user found with given username"
    elif not check_password_hash(user["password"], password):
        error = "Incorrect password"

    if error is None:
        session.clear()
        session["user_id"] = user["id"]
        return redirect(url_for("index"))

    flash(error)
    return render_template("auth/login.html")


@bp.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


def login_required(view):
    @functools.wrap(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)
    return wrapped_view



