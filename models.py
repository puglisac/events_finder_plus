from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    db.app = app
    db.init_app(app)

# models go below



class User(UserMixin, db.Model):
    """User."""

    def __repr__(self):
        """Show info about user."""

        u = self
        return f"<User {u.id} {u.email} {u.first_name} {u.last_name}>"

    __tablename__ = "users"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    email = db.Column(db.Text,
                      nullable=False,
                      unique=True)
    password = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    location = db.Column(db.Text, nullable=False)
    events = db.relationship(
        'Event', secondary='users_events', backref='users')


    @classmethod
    def register(cls, email, pwd, first, last, loc):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return cls(email=email, password=hashed_utf8, first_name=first, last_name=last, location=loc)

    @classmethod
    def authenticate(cls, email, pwd):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        u = User.query.filter_by(email=email).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return u
        else:
            return False

    @classmethod
    def change_password(cls, email, password):
        user = cls.query.filter_by(email=email).first()

        if user:
            hashed_pwd = bcrypt.generate_password_hash(
                password).decode('UTF-8')
            user.password = hashed_pwd
            return user

        return False

class Event(db.Model):
    """Event."""

    def __repr__(self):
        """Show info about an event."""

        e = self
        return f"<Event {e.id}>"

    __tablename__ = "events"

    id = db.Column(db.Text,
                   primary_key=True)


class UsersEvents(db.Model):
    """UsersEvents."""

    __tablename__ = "users_events"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                        nullable=False)
    event_id = db.Column(db.Text, db.ForeignKey('events.id'),
                         nullable=False)
