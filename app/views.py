from flask import render_template, flash
from app import app
from datetime import datetime as dt
import time
import json

day_length = 86400
with open('app/sem2topics.json') as f:
    topics = json.loads(f.read())

#the day given by times refers to 12AM of the morning of the day of class
with open('app/sem2times.json') as f:
    times = json.loads(f.read())

if topics['num-classes'] != times['num-classes']:
    raise Exception('Mismatch between number of topics and number of days')

topics = topics['data']
localtimes = [time.mktime(dt.strptime(t, "%m/%d/%y").timetuple()) for t in times['data']]

#Zip time info into the topics dictionary
time_iter = iter(localtimes)
for unit in topics:
    for cl in unit['unit-classes']:
        t = time_iter.next()
        cl['time'] = t
        dt_obj = dt.fromtimestamp(t)
        cl['day-of-week'] = int(dt_obj.strftime("%w")) #1 = Monday, 2 = Tuesday, ..., 5 = Friday
        cl['week-of-year'] = int(dt_obj.strftime("%W"))
        cl['pretty-time'] = dt_obj.strftime("%A: %B %d, %Y")

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
        title = 'Home')

@app.route('/loghw')
def me():
    current_time = time.time()

    current_dt = dt.fromtimestamp(current_time)
    day_of_week = int(current_dt.strftime("%w"))
    week_of_year = int(current_dt.strftime("%W"))

    current_week_classes = getClassesFromWeek(week_of_year)

    flash("It is {0}".format(current_dt.strftime("%A, %B %d, %Y at %I:%M:%S %p")))

    return render_template('loghw.html',
        title='Class Log and HW',
        db=topics,
        classes=current_week_classes,
        day_of_week=day_of_week)

def getClassesFromWeek(weekNumber):
    classes = [None, None, None, None, None]
    for unit in topics:
        for cl in unit['unit-classes']:
            if cl['week-of-year'] == weekNumber:
                day = cl['day-of-week']
                if day == 1: #Monday
                    classes[0] = cl
                elif day == 2: #Tuesday
                    classes[1] = cl
                elif day == 3: #Wednesday
                    classes[2] = cl
                elif day == 4: #Thursday
                    classes[3] = cl
                elif day == 5: #Friday
                    classes[4] = cl
    return classes
    
#Returns a class object if localtime is within one day of a classes' associated time, or None otherwise
def getClassFromTime(localtime):
    for unit in topics:
        for cl in unit['unit-classes']:
            if localtime - cl['time'] < 86400:
                return cl
            elif localtime < cl['time']:
                return None
    return None