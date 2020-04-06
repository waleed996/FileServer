# File Server

This is a simple File Server Python Flask application with features like sign up, sign in, authentication and file permission management.

## Installation

Before proceeding with the installation please make sure that you have sqlite database and Python 3.8 or greater installed.

Please follow the steps below to setup the application server.

1 . Clone the repository in your local system and make sure you are on master branch.

2 . Go to the directory where you cloned the repository and open a terminal.

3 . Type the following command to install the application requirements

```bash
pip install -r requirements.txt
```
4 . Finally run the start.sh script in the cloned project to start the server.

```bash
./start.sh
```

## Note

Please find the File Server API Postman collection in the cloned repository and import it for testing/evaluation, please go through the request descriptions to get yourself started. The swagger documentation is not functional.


## Explanation of Design


## 1 . Database

The database i used for this application server is an sqlite database with an ORM based open source project flask-sqlalchemy(2.4.1) which is widely used by the community. Following are the reasons why i used sqlite.

1 . It is a light database and has good performance.

2 . The database schema required for the given requirements is a small one. There are only 4 tables required so it makes sense to use a light weight database.

The database schema i have used has separate tables for user types and file permissions which are referred to the user and file tables through a foreign key relationship. This allows the application to be scale able if there is a need to add more user types and file permissions in the future

## 2 . File Storage

The application manages file storage using a directory structure. Each user has his own directory inside the file storage. The status of the files, their ownership information and their access privileges are stored inside the database.

Files that have been made public by their owners are marked public in the database which then allows all users to view. But only the owner can update or delete the file.

## 3 . Authentication

For user authentication i have used another commonly used open source project Flask-JWT(0.3.2). This project uses advanced cryptography techniques to create signed tokens for each user which are required in each request as they serve as an identity to which user is making the request. The tokens generated also have a time limit(configurable using env variables in start.sh). Another good thing about using Flask-JWT is that it does not create additional tables for authentication purposes in the database. It also provides the current user making the request through a proxy when the jwt_required decorator is used on the view.


