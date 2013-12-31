from flask import render_template, flash, redirect, url_for
from app import app
from os import urandom
from datetime import datetime
import json

with open('app/topics.json') as f:
    topics = json.loads(f.read())
# times = json.loads('times.json')


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
        title = 'Home')

@app.route('/loghw')
def me():
    return render_template('loghw.html',
        title='Class Log and HW',
        db=topics)