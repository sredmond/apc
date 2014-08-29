from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bcrypt import Bcrypt
from momentjs import momentjs
from rendering_options import options

app = Flask(__name__)
app.config.from_object('config')
app.jinja_env.globals['momentjs'] = momentjs #Allow Jinja templates to use momentjs

for key, value in options.iteritems():
	app.jinja_env.globals[key] = value

# Tell Jinja to strip whitespace
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

db = SQLAlchemy(app)

#Generate an encrypter
bcrypt = Bcrypt(app)
'''
bcrypt has two essential functions:
pw_hash = bcrypt.generate_password_hash('some_string')
bcrypt.check_password_hash(pw_hash, 'some_string) returns True
'''

from app import views, models