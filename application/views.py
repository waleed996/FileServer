"""
REST Endpoints for the application.
"""

import os
import uuid

from flask import current_app as app
from flask import jsonify, make_response, request
from flask_jwt import jwt_required
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

    if 'files' not in request.files:
        return make_response(jsonify({'error':'expected key "files" in form data'})
                            , 400)

    if request.files['files'].filename == '':
        return make_response(jsonify({'error':'no file attatched'}), 400)


    for file in request.files.getlist('files'):
        file_id = str(uuid.uuid4()) + '_' + file.filename
        file.save(os.path.join(FILES_UPLOAD_DIR, file_id))

        #new_file = File(id=file_id, )


    return make_response(jsonify({'status':'success'}), 200)
