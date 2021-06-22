"""Capstone 1 Application"""


from flask import Flask, request, render_template, redirect, flash, session, jsonify, g
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post
from forms import AddUserForm, LoginUserForm, EditUserForm, PostForm
from sqlalchemy.exc import IntegrityError
import os
import psycopg2

import pdb

from spotify_client import *

CURR_USER_KEY = "curr_user"
DATABASE_URL = os.environ["DATABASE_URL"]
conn = psycopg2.connect(DATABASE_URL, sslmode="require")
SECRET_KEY = os.environ["APP_SECRET_KEY"]

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = SECRET_KEY
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

# Can use below to call class.
# Example: "spotify.get_client_credentials()""
client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")
spotify = SpotifyAPI(client_id, client_secret)


@app.before_request
def add_user_to_g():
    """If logged in, add curr_user to Flask global(g)"""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Login User"""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout User"""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


# Homepage/Create "authorization" link out to reddit.com:
@app.route("/")
def homepage():
    """Show homepage"""

    if g.user:
        following_ids = [f.id for f in g.user.following] + [g.user.id]

        filtered_posts = (
            Post.query.filter(Post.user_id.in_(following_ids))
            .order_by(Post.timestamp.desc())
            .limit(50)
            .all()
        )

        for post in filtered_posts:
            post.song = spotify.get_resource(post.spotify_id, resource_type="tracks")

        liked_post_ids = [p.id for p in g.user.likes]

        return render_template(
            "home.html",
            posts=filtered_posts,
            likes=liked_post_ids,
        )
    else:
        return render_template("anon-home.html")


######### User Signup/Login/Logout Routes Below: #########

# User signup
@app.route("/signup", methods=["GET", "POST"])
def user_signup():
    """User Signup Page.
    Create new User & Add to DB, then redirect to Homepage.
    """

    form = AddUserForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Oops! Username is already taken. Please pick another one!", "danger")
            return render_template("users/signup.html", form=form)

        do_login(user)
        flash(f"Welcome to the MuMe Community, {user.username}!", "success")
        return redirect("/")

    else:
        return render_template("users/signup.html", form=form)


# User login
@app.route("/login", methods=["GET", "POST"])
def user_login():
    """User Login Page.
    Handles User Login Form
    """

    form = LoginUserForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}. Welcome back!", "success")
            return redirect("/")
        flash("Invalid username and/or password.", "danger")

    return render_template("users/login.html", form=form)


# User logout
@app.route("/logout")
def user_logout():
    """Handles User Logout"""

    do_logout()
    flash(f"You successfully logged out! See you next time!", "success")

    return redirect("/login")


######### General User Routes Below: #########

# List of Users
@app.route("/users")
def list_users():
    """Lists Users"""

    search = request.args.get("q")

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    if not g.user:
        flash("You must signup/login to complete this action.", "danger")
        return redirect("/")

    return render_template("users/list_users.html", users=users)


# Show User
@app.route("/users/<int:user_id>")
def show_user(user_id):
    """Show User Profile"""

    user = User.query.get_or_404(user_id)

    posts = (
        Post.query.filter(Post.user_id == user_id)
        .order_by(Post.timestamp.desc())
        .limit(50)
        .all()
    )

    for post in posts:
        post.song = spotify.get_resource(post.spotify_id, resource_type="tracks")

    likes = [post.id for post in user.likes]

    return render_template("users/show_user.html", user=user, posts=posts, likes=likes)


# Edit/Update User Profile
@app.route("/users/profile", methods=["GET", "POST"])
def user_profile():
    """Show and handle form to edit/update CURR_USER profile"""

    if not g.user:
        flash("Oops! You are unauthorized to complete this action.", "danger")
        return redirect("/")

    user = g.user
    form = EditUserForm(obj=user)

    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):
            user.username = form.username.data
            user.email = form.email.data
            user.image_url = form.image_url.data
            user.bio = form.bio.data

            db.session.commit()
            return redirect(f"/users/{user.id}")

        flash("Oops! You are unauthorized to complete this action.", "danger")

    return render_template("users/edit_user.html", user_id=user.id, form=form)


# Follow other users
@app.route("/users/follow/<int:follow_id>", methods=["POST"])
def add_follow(follow_id):
    """Add a Follow for CURR_USER"""

    if not g.user:
        flash("Oops! You are unauthorized to complete this action.", "danger")
        return redirect("/")

    followed_user = User.query.get_or_404(follow_id)
    g.user.following.append(followed_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


# Unfollow other users
@app.route("/users/unfollow/<int:follow_id>", methods=["POST"])
def unfollow(follow_id):
    """Have CURR_USER unfollow other user"""

    if not g.user:
        flash("Oops! You are unauthorized to complete this action.", "danger")
        return redirect("/")

    followed_user = User.query.get_or_404(follow_id)
    g.user.following.remove(followed_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


# Show who User is following
@app.route("/users/<int:user_id>/following")
def user_following(user_id):
    """Show other users that CURR_USER is following"""

    if not g.user:
        flash("Oops! You are unauthorized to complete this action.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template("users/following.html", user=user)


# Show who is following User
@app.route("/users/<int:user_id>/followers")
def user_followers(user_id):
    """Show followers of CURR_USER"""

    if not g.user:
        flash("Oops! You are unauthorized to complete this action.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template("users/followers.html", user=user)


# User Likes Routes:
@app.route("/users/add_like/<int:post_id>", methods=["POST"])
def add_like(post_id):
    """Allow CURR_USER to add a like to other users' Post(s)"""

    if not g.user:
        flash("Oops! You are unauthorized to complete this action.", "danger")
        return redirect("/")

    liked_post = Post.query.get_or_404(post_id)

    if liked_post in g.user.likes:
        g.user.likes = [like for like in g.user.likes if like != liked_post]
    else:
        g.user.likes.append(liked_post)

    db.session.commit()

    return redirect("/")


@app.route("/users/<int:user_id>/likes", methods=["GET"])
def show_user_likes(user_id):
    """Show Post(s) that CURR_USER liked"""

    if not g.user:
        flash("Oops! You are unauthorized to complete this action.", "danger")
        return redirect("/")

    following_ids = [f.id for f in g.user.following] + [g.user.id]

    filtered_posts = (
        Post.query.filter(Post.user_id.in_(following_ids))
        .order_by(Post.timestamp.desc())
        .limit(50)
        .all()
    )

    for post in filtered_posts:
        post.song = spotify.get_resource(post.spotify_id, resource_type="tracks")

    liked_post_ids = [p.id for p in g.user.likes]

    user = User.query.get_or_404(user_id)
    return render_template(
        "users/likes.html",
        user=user,
        userLikes=user.likes,
        posts=filtered_posts,
        likedPostIds=liked_post_ids,
    )


# Delete User
@app.route("/users/delete", methods=["POST"])
def delete_user():
    """Deletes User"""

    if not g.user:
        flash("Oops! You are unauthorized to complete this action.", "danger")
        return redirect("/")

    do_logout()
    flash("We'll miss you here at MuMe!", "primary")

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")


######### General Post Routes Below: #########


@app.route("/songs", methods=["GET", "POST"])
def get_songs():

    song_query = request.json.get("songQuery")
    songs = spotify.search(f"{song_query}")

    return jsonify(songs=songs)


@app.route("/posts/new", methods=["GET", "POST"])
def new_post():
    """Create new blog post"""
    if not g.user:
        flash("Oops! You are unauthorized to complete this action.", "danger")
        return redirect("/")

    form = PostForm()

    if form.validate_on_submit():
        song_query = request.form["song_query"]

        if not song_query:
            post = Post(text=form.text.data)
            g.user.posts.append(post)
            db.session.commit()
        else:
            song_id = request.form["song-data"]
            post = Post(text=form.text.data, spotify_id=song_id)
            g.user.posts.append(post)
            db.session.commit()

        return redirect(f"/posts/{post.id}")

    return render_template("posts/new_post.html", form=form)


@app.route("/posts/<int:post_id>", methods=["GET"])
def show_post(post_id):
    """Show CURR_USER post"""

    post = Post.query.get(post_id)
    song = spotify.get_resource(post.spotify_id, resource_type="tracks")

    return render_template(
        "posts/show_post.html",
        post=post,
        song_name=song["name"],
        artist_name=song["artists"][0]["name"],
        song_cover_art=song["album"]["images"][2]["url"],
        song_url=song["external_urls"]["spotify"],
        artist_url=song["artists"][0]["external_urls"]["spotify"],
    )


@app.route("/posts/<int:post_id>/delete", methods=["POST"])
def delete_post(post_id):
    """Delete CURR_USER post"""

    if not g.user:
        flash("Oops! You are unauthorized to complete this action.", "danger")
        return redirect("/")

    post = Post.query.get_or_404(post_id)

    db.session.delete(post)
    db.session.commit()

    return redirect(f"/users/{g.user.id}")