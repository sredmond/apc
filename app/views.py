from flask import render_template, flash, redirect, url_for
from app import app
from os import urandom
from datetime import datetime
import json

with open('app/topics.json') as f:
    topics = json.loads(f.read())

#the day given by times refers to 12AM of the morning of the day of class
with open('app/times.json') as f:
    times = json.loads(f.read())

if topics['num_classes'] != times['num_classes']:
    raise Exception('Mismatch between number of topics and number of days')

topics = topics['data']
localtimes = [time.mktime(dt.strptime(t, "%m/%d/%y").timetuple()) for t in times['data']]
#XXX Zip topics and times into one object

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

#Returns a class object if localtime is within one day of a classes' associated time, or None otherwise
def getClassFromTime(localtime):
    pass