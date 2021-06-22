from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

DEFAULT_PIC = "/static/images/default-pic.png"


def connect_db(app):
    """Connect db to Flask app. I should call this in Flask app."""

    db.app = app
    db.init_app(app)


class Follows(db.Model):
    """Personal User following Other users & Other users following Personal User"""

    __tablename__ = "follows"

    user_being_followed_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )

    user_following_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )


class Likes(db.Model):
    """User Likes on Posts"""

    __tablename__ = "likes"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))

    post_id = db.Column(db.Integer, db.ForeignKey("posts.id", ondelete="CASCADE"))


class User(db.Model):
    """User Model"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.Text, nullable=False, unique=True)

    email = db.Column(db.Text, nullable=False, unique=True)

    password = db.Column(db.Text, nullable=False)

    image_url = db.Column(db.Text, default=DEFAULT_PIC)

    bio = db.Column(db.Text)

    location = db.Column(db.Text)

    posts = db.relationship("Post")

    likes = db.relationship("Post", secondary="likes")

    following = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.user_following_id == id),
        secondaryjoin=(Follows.user_being_followed_id == id),
    )

    followers = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.user_being_followed_id == id),
        secondaryjoin=(Follows.user_following_id == id),
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    def is_followed_by(self, other_user):
        """Is User being followed by other_user?"""

        found_user_list = [user for user in self.followers if user == other_user]
        return len(found_user_list) == 1

    def is_following(self, other_user):
        """Is User following other_user?"""

        found_user_list = [user for user in self.following if user == other_user]
        return len(found_user_list) == 1

    @classmethod
    def signup(cls, username, email, password, image_url):
        """Signup User.

        Hash password and add User to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode("UTF-8")

        user = User(
            username=username, email=email, password=hashed_pwd, image_url=image_url
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Make sure User matches `username` & `password`

        If User cannot match `username` & `password`, return False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Post(db.Model):
    """User Post"""

    __tablename__ = "posts"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    text = db.Column(db.String(150), nullable=False)

    spotify_id = db.Column(db.Text, nullable=True)

    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    user = db.relationship("User")
