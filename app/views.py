from flask import render_template, flash, redirect, url_for
from app import app
from datetime import datetime as dt
import time
from calendar import timegm
import json

pst_offset = 8 * 60 * 60

with open('app/static/json/topics.json') as f:
	topics = json.loads(f.read())

with open('app/static/json/times.json') as f:
	times = json.loads(f.read())

with open('app/static/json/carouselImages.json') as f:
	carousel_images = json.loads(f.read())

#Seconds since epoch at which a new PST day w/ physics begins
epoch_day_offsets = [timegm(time.strptime(t, "%m/%d/%y")) for t in times]

#Zip time info into the topics dictionary
try:
	time_iter = iter(epoch_day_offsets)
	for unit in topics:
		for cl in unit['unit-classes']:
			t = time_iter.next() #Seconds since epoch of a new UTC day - could throw an error
			dt_obj = dt.utcfromtimestamp(t) #Datetime representing the local date and time
			cl['time'] = t + pst_offset #Seconds since epoch of a new PST day
			cl['dt-obj'] = dt_obj
			cl['day-of-week'] = int(dt_obj.strftime("%w")) #1 = Monday, 2 = Tuesday, ..., 5 = Friday
			cl['week-of-year'] = int(dt_obj.strftime("%W"))
except Exception:
	print "Oh no! We've encountered an error."
	raise Exception("There are too many classes in the topics JSON file and not enough dates in the times JSON file. Ensure that there are at least as many dates as there are Physics classes.")

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html',
		title = 'Home',
		carousel_images=carousel_images)

@app.route('/loghw')
def me():
	seconds_since_epoch = time.time()
	current_datetime = dt.utcfromtimestamp(seconds_since_epoch - pst_offset)

	current_day_of_week = int(current_datetime.strftime("%w")) #1 is monday
	current_week_of_year = int(current_datetime.strftime("%W"))
	current_week_classes = getClassesFromWeek(current_week_of_year)

	# flash("It is {0} PST".format(current_datetime.strftime("%A, %B %d, %Y at %I:%M:%S %p")), category='info')
	flash("Beyond simple harmonic motion, the class information was copied from last year's schedule. Dr. Dann will have to update it to correspond to this year (e.g. correct days for HIWW, etc). Once he does, this warning message will disappear forever.",category='warning')

	return render_template('loghw.html',
		title='Class Log and HW',
		db=topics,
		classes=current_week_classes,
		day_of_week=current_day_of_week)

@app.route('/refreshjson')
def refreshJSON():
	global topics
	global times
	global carousel_images
	with open('app/static/json/topics.json') as f:
		newTopics = json.loads(f.read())
	with open('app/static/json/times.json') as f:
		newTimes = json.loads(f.read())
	with open('app/static/json/carouselImages.json') as f:
		newImages = json.loads(f.read())
	epoch_day_offsets = [timegm(time.strptime(t, "%m/%d/%y")) for t in newTimes]
	try:
		time_iter = iter(epoch_day_offsets)
		for unit in newTopics:
			for cl in unit['unit-classes']:
				t = time_iter.next() #Seconds since epoch of a new UTC day - could throw an error
				dt_obj = dt.utcfromtimestamp(t) #Datetime representing the local date and time
				cl['time'] = t + pst_offset #Seconds since epoch of a new PST day
				cl['dt-obj'] = dt_obj
				cl['day-of-week'] = int(dt_obj.strftime("%w")) #1 = Monday, 2 = Tuesday, ..., 5 = Friday
				cl['week-of-year'] = int(dt_obj.strftime("%W"))
	except Exception:
		flash("Oh no! There are too many classes in the topics JSON file and not enough dates in the times JSON file. Ensure that there are at least as many dates as there are Physics classes before trying again.", category='error')
		return redirect(url_for('index'))
	topics = newTopics
	times = newTimes
	carousel_images = newImages
	flash('JSON files successfully updated')
	return redirect(url_for('index'))

#Not the fastest, but it'll be fine
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