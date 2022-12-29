from flask import Blueprint, render_template, request, flash, g, abort, redirect, url_for
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)


@bp.route("/")
def index():
    db = get_db()
    posts = db.execute("""
        SELECT p.id, p.title, p.body, p.created, p.author_id, u.username
        FROM post AS p 
           JOIN user AS u ON p.author_id = u.id 
        ORDER BY created DESC
    """).fetchall()
    return render_template("blog/index.html", posts=posts)


@bp.route("/create")
@login_required
def create_get():
    return render_template("blog/create.html")


@bp.post("/create")
@login_required
def create_post():
    # see how this code is very easy to reason about
    title = request.form["title"]
    body = request.form["body"]
    error = None
    if not title:
        error = "Title is required"

    if error is not None:
        flash(error)
        return render_template("blog/create.html")
    else:
        db = get_db()
        db.execute("""
            INSERT INTO post(title, body, author_id)
            VALUES (?, ?, ?)
        """, (title, body, g.user["id"]))
        db.commit()
        return redirect(url_for("blog.index"))


@bp.post('/<int:id>/update')
@login_required
def update_post(id):
    post = get_post(id)
    title = request.form["title"]
    body = request.form["body"]
    error = None

    if not title:
        error = "Title is required"

    if error is not None:
        flash(error)
        return render_template("blog/update.html", post=post)
    else:
        db = get_db()
        db.execute("""
        UPDATE post SET title = ?, body = ? 
        WHERE id = ?
        """, [title, body, id])
        db.commit()
        return redirect(url_for("blog.index"))

@bp.post("/<int:id>/delete")
@login_required
def delete(id):
    post = get_post(id, check_author=True)
    db = get_db()
    db.execute('''
    DELETE FROM post WHERE id = ?
    ''', [id])
    db.commit()
    return redirect(url_for('blog.index'))


@bp.get("/<int:id>/update")
@login_required
def update_get(id):
    post = get_post(id, check_author=True)
    return render_template("blog/update.html", post=post)


def get_post(id, check_author=True):
    post = get_db().execute('''
    SELECT p.id, p.title, p.body, p.author_id, u.username
    FROM post AS p 
        JOIN user AS u ON p.author_id = u.id
    WHERE p.id = ?
    ''', [id]).fetchone()

    if post is None:
        abort(404, f"Post with id {id} does not exist")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post





