import os

basedir = os.path.abspath(os.path.dirname(__file__))

if os.environ.get('DATABASE_URL') is None: #For server
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
else: #For Heroku Configuration
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

SECRET_KEY = os.urandom(24)