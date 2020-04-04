# Environment variables
export FLASK_ENV=development
export FLASK_DEBUG=1
export SQLALCHEMY_DATABASE_URI='sqlite:///../fileserver.db'
export SQLALCHEMY_TRACK_MODIFICATIONS=False
export FILES_UPLOAD_DIRECTORY='/files'

# Flask secret key
export JWT_SECRET_KEY='98SIy52tH1E0B4P6D28T6mqPTKHO8nP3'

# Start flask server
python app.py