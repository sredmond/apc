from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flaskext.bcrypt import Bcrypt
from momentjs import momentjs

app = Flask(__name__)
app.config.from_object('config')
app.jinja_env.globals['momentjs'] = momentjs #Allow Jinja templates to use momentjs

db = SQLAlchemy(app)

#Generate an encrypter
bcrypt = Bcrypt(app)
'''
bcrypt has two essential functions:
pw_hash = bcrypt.generate_password_hash('some_string')
bcrypt.check_password_hash(pw_hash, 'some_string) returns True
'''

from app import views, models