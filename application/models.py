"""
Models for the application.
"""

import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship

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

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    users = relationship('User')


class File(db.Model):
    """Model for files saved by the application"""
    __tablename__ = 'file'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(Integer, ForeignKey('user.id'))
    file_name = Column(String(100), nullable=False)
    file_path = Column(String(200), nullable=False)
    file_access_permission = Column(Integer,
                        ForeignKey('file_permission.id'), nullable=False)
    last_updated = Column(DateTime, unique=True, nullable=False,
                                 default=datetime.datetime.utcnow)
    deleted = Column(Boolean, default=False)


class FilePermission(db.Model):
    """Model for user type permissions"""
    __tablename__ = 'file_permission'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), unique=True, nullable=False)

