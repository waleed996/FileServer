"""
Application and database definition.
"""

import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    "Initializes the flask application, registers the views and swagger ui blueprints."
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS')
    db.init_app(app)

    with app.app_context():
        from . import views
        # Create tables for the models.
        db.create_all()

        return app

