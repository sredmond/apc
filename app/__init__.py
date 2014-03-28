from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flaskext.bcrypt import Bcrypt
from momentjs import momentjs

app = Flask(__name__)
app.config.from_object('config')
app.jinja_env.globals['momentjs'] = momentjs #Allow Jinja templates to use momentjs

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
''' How to use
pw_hash = bcrypt.generate_password_hash('hunter2')
print bcrypt.check_password_hash(pw_hash, 'hunter2')''' # returns True'''

from app import views, models