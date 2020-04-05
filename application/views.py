"""
REST Endpoints for the application.
"""

import os
from datetime import datetime

from flask import current_app as app
from flask import jsonify, make_response, request, send_file
from flask_jwt import current_identity, jwt_required
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import DatabaseError

from . import authentication
from .models import File, FilePermission, UserType, db
from .schemas import FilePermissionSchema, UserSchema, UserTypeSchema
from .urls import URLS

# Create the file upload directory if not exists
FILES_UPLOAD_DIR = os.path.join(app.instance_path,
                    '..' + os.environ.get('FILES_UPLOAD_DIRECTORY'))
os.makedirs(FILES_UPLOAD_DIR, exist_ok=True)


@app.route(URLS.get('GET_USER_TYPES'), methods=['GET'])
#@jwt_required()
def get_user_types():
    """Endpoint to get all available user types"""

    user_types = UserType.query.all()

    user_type_serialized = UserTypeSchema().dump(user_types, many=True)

    return make_response(jsonify({'user_types':user_type_serialized}), 200)


@app.route(URLS.get('CREATE_USER'), methods=['POST'])
def create_user():
    """Endpoint to create a user"""
    try:
        schema = UserSchema()
        new_user = schema.load(request.json, session=db.session)
        new_user.password = pbkdf2_sha256.hash(new_user.password)

        db.session.add(new_user)
        db.session.commit()
        return jsonify(schema.dump(new_user))
    except DatabaseError as err:
        db.session.rollback()
        return make_response(jsonify({
            'error':repr(err)
        }), 400)



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


    user_dir = FILES_UPLOAD_DIR + '/' + str(current_identity.id)
    os.makedirs(user_dir, exist_ok=True)

    messages = []
    errors = []

    for file in request.files.getlist('files'):

        # Check if file already exists
        check_file = File.query.filter_by(file_name=file.filename,
                                          user=current_identity.id,
                                          deleted=False).first()

        if not check_file is None:
            messages.append(f' {check_file.file_name} already uploaded.')
            continue

        try:

            file_id = file.filename
            file.save(os.path.join(user_dir, file_id))

            file_permission = FilePermission.query.filter_by(
                                                   name='revoke').first()

            new_file = File(user=current_identity.id,
                            file_name=file_id,
                            file_path=client_file_path,
                            file_access_permission=file_permission.id,
                            last_updated=datetime.utcnow())

            db.session.add(new_file)
            db.session.commit()

        except DatabaseError as err:
            db.session.rollback()
            errors.append(repr(err))
            continue

    if len(errors) == 0:
        return make_response(jsonify({'message':'Upload complete',
                                      'info':messages,}), 200)

    return make_response(jsonify({'message':'Internal Server Error',
                                  'info':messages,
                                  'error':errors}), 500)


@app.route(URLS.get('GET_FILE'), methods=['GET'])
@jwt_required()
def get_file():
    """Endpoint for user to view/download file."""

    user_dir = FILES_UPLOAD_DIR + '/' + str(current_identity.id)

    file_name = request.form.get('file', default=None)
    if file_name is None:
        return make_response(jsonify({'error':'No file name provided'}), 400)


    admin_users = UserType.query.filter_by(name='admin').first().users

    if current_identity in admin_users:

        user = request.form.get('user', default=None)
        if user is None:
            return make_response(jsonify(
                {'error':'"user" id required.'})
                , 400)

        file = File.query.filter_by(file_name=file_name, user=user,
                                    deleted=False).first()
        if file is None:
            return make_response(jsonify(
                {'error':'No file found.'})
                , 400)

        return send_file(FILES_UPLOAD_DIR + '/' + str(file.user) + '/' +
                        file_name)


    file = File.query.filter_by(file_name=file_name, user=current_identity.id,
                                deleted=False).first()

    # Searching public files with permission 'allow'
    public_files = FilePermission.query.filter_by(name='allow').first().files

    for public_file in public_files:
        if public_file.file_name == file_name:
            return send_file(FILES_UPLOAD_DIR + '/' + str(public_file.user) + '/' + file_name)

    if file is None:
        return make_response(jsonify(
                {'error':'User does not have any file with provided name'})
                , 400)

    return send_file(user_dir + '/' + file_name)


@app.route(URLS.get('DELETE_FILE'), methods=['DELETE'])
@jwt_required()
def delete_file():
    """Endpoint to delete a file."""

    file_name = request.form.get('file_name', default=None)
    if file_name is None:
        return make_response(jsonify(
                                {'error':'"file_name" value required.'}), 400)

    file = File.query.filter_by(file_name=file_name, user=current_identity.id,
                                deleted=False).first()

    if file is None:
        return make_response(jsonify(
                                {'error':'File not found.'}), 400)

    errors = []

    try:
        os.remove(FILES_UPLOAD_DIR + '/' + str(file.user) + '/' + file_name)

        file.deleted = True
        db.session.add(file)
        db.session.commit()

    except DatabaseError as err:
        errors.append(repr(err))
        db.session.rollback()

    if len(errors) == 0:
        return make_response(jsonify(
                                {'message':'File deleted successfully.',}),
                                 200)

    return make_response(jsonify(
                                {'message':'Internal Server Error.',
                                'error':errors}),
                                 500)


@app.route(URLS.get('UPDATE_FILE'), methods=['PATCH'])
@jwt_required()
def update_file():
    """Endpoint to update the file"""

    updated_file = request.files.get('updated_file', default=None)

    if updated_file is None:
        return make_response(jsonify({'error':'No file attatched'}), 400)


    file = File.query.filter_by(file_name=updated_file.filename,
                                user=current_identity.id,
                                deleted=False).first()

    if file is None:
        return make_response(jsonify({'error':'No file found.'}), 400)

    errors = []

    try:
        os.remove(FILES_UPLOAD_DIR + '/' + str(file.user) + '/' +
                                         updated_file.filename)
        updated_file.save(FILES_UPLOAD_DIR + '/' + str(file.user) + '/' +
                                            updated_file.filename)

        file.last_updated = datetime.utcnow()

        db.session.add(file)
        db.session.commit()

    except DatabaseError as err:
        errors.append(repr(err))
        db.session.rollback()

    if len(errors) == 0:
        return make_response(jsonify(
                                {'message':'File updated successfully.',}),
                                 200)

    return make_response(jsonify(
                                {'message':'Internal Server Error.',
                                'error':errors}),
                                 500)



@app.route(URLS.get('GET_FILE_PERMISSION_TYPES'), methods=['GET'])
#@jwt_required()
def get_file_permission_types():
    """Endpoint to get all available file permission types"""

    file_permission_types = FilePermission.query.all()

    file_permission_type_serialized = FilePermissionSchema().dump(
                                        file_permission_types, many=True)

    return make_response(jsonify(
                    {'file_permission_types':file_permission_type_serialized})
                    , 200)



@app.route(URLS.get('UPDATE_FILE_PERMISSION'), methods=['PATCH'])
@jwt_required()
def update_file_permissions():
    """Endpoint to update file permissions."""

#    admin_users = UserType.query.filter_by(name='admin').first().users

#    if current_identity in admin_users:
#        return make_response(
#        {'error':'Admin users have full access by default.'}, 400)


    file_name = request.form.get('file_name', default=None)
    user_email = request.form.get('user_email', default=None)
    action = request.form.get('action', default=None)


    if file_name is None:
        return make_response(jsonify(
                                {'error':'"file_name" value required.'}), 400)
    if user_email is None:
        return make_response(jsonify(
                                {'error':'"user_email" value required.'}), 400)
    if action is None:
        return make_response(jsonify(
                                {'error':'"action" value required.'}), 400)


    if not current_identity.email == user_email:
        return make_response(jsonify(
                {'error':'Email mismatch, please use your account email.'}),
                 400)

    file = File.query.filter_by(file_name=file_name,
                                user=current_identity.id,
                                deleted=False).first()
    if file is None:
        return make_response(jsonify(
            {'error': 'Could not find file, incorrect file_name.'}), 400)

    new_permission = FilePermission.query.filter_by(
                                        name=action).first()
    if new_permission is None:
        return make_response(jsonify(
                        {'error':'"action" value permission does not exist.'}),
                         400)

    file.file_access_permission = new_permission.id

    db.session.add(file)
    db.session.commit()

    return make_response(jsonify(
                        {'message':'Permissions updated successfully.'}), 200)
