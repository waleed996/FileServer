"""
REST Endpoints for the application.
"""

from flask import current_app as app
from flask import jsonify, make_response, request
from marshmallow import ValidationError

from .models import db
from .schemas import UserSchema
from .urls import URLS


@app.route(URLS.get('CREATE_USER'), methods=['POST'])
def create_user():
    """Endpoint to create a user"""
    try:
        schema = UserSchema()
        new_user = schema.load(request.json)
        db.session.add(new_user)
        db.session.commit()
        return jsonify(schema.dump(new_user))
    except ValidationError as err:
        return make_response(err.messages)
