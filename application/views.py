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
from .models import File, db, User, UserType, FilePermission
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

        file_permission = FilePermission.query.filter_by(name='revoke').first()

        new_file = File(user=current_identity.id,
                        file_name=file_id,
                        file_path=client_file_path,
                        file_access_permission=file_permission.id,
                        last_updated=datetime.utcnow())

        db.session.add(new_file)
        db.session.commit()


    return make_response(jsonify({'status':'upload complete'}), 200)


@app.route(URLS.get('UPDATE_FILE_PERMISSION'), methods=['GET'])
@jwt_required()
def update_file_permissions():
    """Endpoint to update file permissions."""

    admin_users = UserType.query.filter_by(name='admin').first().users

    if current_identity in admin_users:
        return make_response(
            {'error':'You are an admin user, admin users already have full access.'},
            400
        )


    if 'fileId' not in request.json:
        return make_response(jsonify(
                                {'error':'"fileId" value required.'}), 400)
    if 'userEmail' not in request.json:
        return make_response(jsonify(
                                {'error':'"userEmail" value required.'}), 400)
    if 'action' not in request.json:
        return make_response(jsonify(
                                {'error':'"action" value required.'}), 400)


    if not current_identity.email == request.json['userEmail']:
        return make_response(jsonify(
                {'error':'Email mismatch, please use your account email.'}), 400)

    file = File.query.filter_by(file_name=request.json['fileId'],
                                             user=current_identity.id).first()
    if file is None:
        return make_response(jsonify(
            {'error': 'Could not find file, incorrect fileId.'}), 400)

    new_permission = FilePermission.query.filter_by(
                                        name=request.json['action']).first()
    if new_permission is None:
        return make_response(jsonify(
                            {'error':'"action" value permission does not exist.'})
                            , 400)

    file.file_access_permission = new_permission.id

    db.session.add(file)
    db.session.commit()

    return make_response(jsonify(
                        {'message':'Permissions updated successfully.'}), 200)


