"""
Models for the application.
"""

import datetime

from . import db


class User(db.Model):
    """Model for application users."""
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    bio = db.Column(db.String(200), unique=False, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_type = db.relationship('UserType', backref='User', lazy=True)


class UserType(db.Model):
    """Model for user types supported by application."""
    __tablename__ = 'usertype'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
