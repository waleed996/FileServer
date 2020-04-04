"""
Application authentication module.
"""

from datetime import timedelta
from os import environ

from flask import current_app as app
from flask_jwt import JWT
from passlib.hash import pbkdf2_sha256

from .models import User


def authenticate(username, password):
    """User authentication handler."""
    user = User.query.filter_by(username=username).first()
    if user and pbkdf2_sha256.verify(password, user.password):
        return user


def identity(payload):
    """User identity handler."""
    user_id = payload['identity']
    return User.query.get(user_id)

app.config['SECRET_KEY'] = environ.get('JWT_SECRET_KEY')
app.config['JWT_AUTH_URL_RULE'] = environ.get('JWT_AUTH_URL_RULE')
app.config['JWT_EXPIRATION_DELTA'] = timedelta(
                    seconds=int(environ.get('JWT_EXPIRATION_DELTA')))

jwt = JWT(app, authenticate, identity)
