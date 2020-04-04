"""
REST Endpoints for the application.
"""

import os
from datetime import datetime

from flask import current_app as app
from flask import jsonify, make_response, request
from flask_jwt import current_identity, jwt_required
from marshmallow import ValidationError
from passlib.hash import pbkdf2_sha256

from . import authentication
from .models import File, db
from .schemas import UserSchema
from .urls import URLS

# Create the file upload directory if not exists
FILES_UPLOAD_DIR = os.path.join(app.instance_path,
                    '..' + os.environ.get('FILES_UPLOAD_DIRECTORY'))
os.makedirs(FILES_UPLOAD_DIR, exist_ok=True)


@app.route(URLS.get('CREATE_USER'), methods=['POST'])
def create_user():
    """Endpoint to create a user"""
    try:
        schema = UserSchema()
        new_user = schema.load(request.json)
        new_user.password = pbkdf2_sha256.hash(new_user.password)

        db.session.add(new_user)
        db.session.commit()
        return jsonify(schema.dump(new_user))
    except ValidationError as err:
        return make_response(err.messages, 400)



@app.route(URLS.get('UPLOAD_FILE'), methods=['POST'])
@jwt_required()
def upload_file():
    """Endpoint to upload a file"""

    client_file_path = request.form.get('path', default=None)

    if client_file_path is None:
        return make_response(jsonify(
                    {'error':'expected key "path" in form data'}), 400)

    if len(request.files.getlist('files')) == 0:
        return make_response(jsonify(
                    {'error':'expected key "files" in form data'}), 400)

    if request.files['files'].filename == '':
        return make_response(jsonify({'error':'no file attatched'}), 400)


    user_dir = FILES_UPLOAD_DIR + '/' +str(current_identity.id)
    os.makedirs(user_dir, exist_ok=True)


    for file in request.files.getlist('files'):

        file_id = file.filename
        file.save(os.path.join(user_dir, file_id))

        new_file = File(user=current_identity.id,
                        file_name=file_id,
                        file_path=client_file_path,
                        last_updated=datetime.utcnow())

        db.session.add(new_file)
        db.session.commit()


    return make_response(jsonify({'status':'upload complete'}), 200)
