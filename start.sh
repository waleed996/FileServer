# Environment variables
export FLASK_ENV=development
export FLASK_DEBUG=1
export SQLALCHEMY_DATABASE_URI="sqlite:///../fileserver.db"

# Start flask server
python app.py