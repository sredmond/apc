import os

basedir = os.path.abspath(os.path.dirname(__file__))

if 'HEROKU' in os.environ:
	timezone_correction = -8
else:
	timezone_correction = 0

SECRET_KEY = os.urandom(24)