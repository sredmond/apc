import os

basedir = os.path.abspath(os.path.dirname(__file__))

if os.environ.get('DATABASE_URL') is None:  # Production
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
else: # Heroku
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

SECRET_KEY = os.urandom(24)
with open('.env','r') as f:
	lines = f.read().split('\n')
	d = {line.split('=')[0]:line.split('=')[1] for line in lines}
	ADMIN_USERNAME = d.get('ADMIN_USERNAME')
	ADMIN_PASSWORD = d.get('ADMIN_PASSWORD')