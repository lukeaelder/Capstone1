"""SQLALchemy models for app."""

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

bcrypt = Bcrypt()
db = SQLAlchemy()

class User(db.Model):
    """User in app."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    username = db.Column(db.Text, nullable = False, unique = True)
    password = db.Column(db.Text, nullable = False)
    email = db.Column(db.Text, nullable = False, unique = True)
    total_reviews = db.Column(db.Integer, nullable = False, default = 0)
    image_url = db.Column(db.Text)
    joined = db.Column(db.DateTime, nullable = False, default = datetime.utcnow())
    bio = db.Column(db.Text)

    @classmethod
    def signup(cls, username, email, password,):
        """Sign up user. Hashes password and adds user to system. """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.
        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
        return False

    favorites = db.relationship("Favorite", backref="user")
    lists = db.relationship("List", backref="user")


class Movie(db.Model):
    """Basic information of movies for list, bookmarks, and favorites."""

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, nullable = False, primary_key = True)
    poster_image = db.Column(db.Text)
    backdrop_image = db.Column(db.Text)
    overview = db.Column(db.Text)
    title = db.Column(db.Text)
    year = db.Column(db.Text)


class List(db.Model):
    """List created by users."""

    __tablename__ = "lists"

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"))
    title = db.Column(db.Text)
    description = db.Column(db.Text)
    image = db.Column(db.Text)
    created = db.Column(db.DateTime, nullable = False, default = datetime.utcnow())
    last_updated = db.Column(db.DateTime, nullable = False, default = datetime.utcnow())
    total_movies = db.Column(db.Integer, nullable = False)

class ListMovie(db.Model):
    """Movies and position for movies in list."""

    __tablename__ = "list_movies"

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    list_id = db.Column(db.Integer, db.ForeignKey("lists.id", ondelete="cascade"))
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.movie_id", ondelete="cascade"))
    position = db.Column(db.Integer, nullable = False)


class Watchlist(db.Model):
    """Watchlist for a user."""

    __tablename__ = "watchlists"

    __table_args__ = (
        db.UniqueConstraint('user_id', 'movie_id'),
    )

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"))
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.movie_id", ondelete="cascade"))


class Favorite(db.Model):
    """Favorites for a user."""

    __tablename__ = "favorites"

    __table_args__ = (
        db.UniqueConstraint('user_id', 'movie_id'),
    )

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"))
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.movie_id", ondelete="cascade"))


class Review(db.Model):
    """Review by user for a movie."""

    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    username = db.Column(db.Text)
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.movie_id", ondelete="cascade"))
    title = db.Column(db.Text, nullable = False)
    body = db.Column(db.Text, nullable = False)
    rating = db.Column(db.Integer, nullable = False)
    created = db.Column(db.DateTime, nullable = False, default = datetime.utcnow())

def connect_db(app):
    """Connect app to db."""

    db.app = app
    db.init_app(app)
