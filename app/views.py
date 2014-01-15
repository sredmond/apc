from flask import render_template, flash
from app import app
from datetime import datetime as dt
from datetime import timedelta
import time
from calendar import timegm
import json
from config import timezone_correction

day_length = 86400
pst_offset = -8 * 60 * 60
with open('app/sem2topics.json') as f:
	topics = json.loads(f.read())

#the day given by times refers to 12AM of the morning of the day of class
with open('app/sem2times.json') as f:
	times = json.loads(f.read())

if topics['num-classes'] != times['num-classes']:
	raise Exception('Mismatch between number of topics and number of days')

topics = topics['data']

#Seconds since epoch at which a new PST day w/ physics begins
epoch_day_offsets = [timegm(time.strptime(t, "%m/%d/%y")) for t in times['data']]

#Zip time info into the topics dictionary
time_iter = iter(epoch_day_offsets)
for unit in topics:
	for cl in unit['unit-classes']:
		t = time_iter.next()
		dt_obj_utc = dt.utcfromtimestamp(t) #The PST datetime object (we avoid using the PST tzinfo classes) 
		cl['dt-obj-utc'] = dt_obj_utc
		cl['unix-time'] = t #Seconds since epoch at which the datetime we want (at midnight) begins in UTC
		cl['pst-time'] = t + pst_offset#Seconds since epoch at which this class day begins
		dt_obj = dt.utcfromtimestamp(t) #The PST datetime object (we avoid using the PST tzinfo classes)
		cl['moment-dt-obj'] = dt.utcfromtimestamp(t + pst_offset)
		cl['day-of-week'] = int(dt_obj.strftime("%w")) #1 = Monday, 2 = Tuesday, ..., 5 = Friday
		print cl['day-of-week']
		cl['week-of-year'] = int(dt_obj.strftime("%W"))
		cl['pretty-time'] = dt_obj.strftime("%A: %B %d, %Y")

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html',
		title = 'Home')

@app.route('/loghw')
def me():
	seconds_since_epoch = time.time()
	local_datetime = dt.utcfromtimestamp(seconds_since_epoch + pst_offset)

	current_day_of_week = int(local_datetime.strftime("%w")) #1 is monday

	current_week_of_year = int(local_datetime.strftime("%W"))
	current_week_classes = getClassesFromWeek(current_week_of_year)

	flash("It is {0} PST".format(local_datetime.strftime("%A, %B %d, %Y at %I:%M:%S %p")))

	return render_template('loghw.html',
		title='Class Log and HW',
		db=topics,
		classes=current_week_classes,
		day_of_week=current_day_of_week)

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