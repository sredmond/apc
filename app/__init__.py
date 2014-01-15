import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from momentjs import momentjs

app = Flask(__name__)
app.config.from_object('config')

app.jinja_env.globals['momentjs'] = momentjs #Allow Jinja templates to use momentjs

from app import views