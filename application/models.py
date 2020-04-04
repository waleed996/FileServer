"""
Models for the application.
"""

import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from . import db


class User(db.Model):
    """Model for application users."""
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(80), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    bio = Column(String(200), unique=False, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user_type = Column(Integer, ForeignKey('usertype.id'))

    def __repr__(self):
        return f'<User id:{self.id} , username:{self.username}'


class UserType(db.Model):
    """Model for user types supported by application."""
    __tablename__ = 'usertype'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True, nullable=False)
