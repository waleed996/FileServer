"""
Application and database definition.
"""

import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint

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

        ### swagger specific ###
        SWAGGER_URL = '/swagger'
        API_URL = '/static/swagger.yaml'
        SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
            SWAGGER_URL,
            API_URL,
            config={
                'app_name': "File Server Application"
            }
        )
        ### end swagger specific ###

        app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

        return app
