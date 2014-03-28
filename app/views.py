'''
TODO
Form validation! I need to make sure Dr. Dann doesn't enter any weird html
Security! Can't give admin access to everyone.
Gotta make the rendering_options universal
'''

#Import useful packages and objects
from flask import render_template, flash, redirect, url_for, request
from app import app, db
from models import Unit, Class, CarouselItem
from datetime import datetime as dt
import time
from calendar import timegm
import json
from rendering_options import *

#8 hours, in seconds
pst_offset = 8 * 60 * 60

with open('app/static/json/topics.json') as f:
  topics = json.loads(f.read())

with open('app/static/json/times.json') as f:
  times = json.loads(f.read())

with open('app/static/json/carousel_items.json') as f:
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
@app.route('/index/')
def index():
  return render_template('index.html',
    title = 'Home',
    carousel_items=CarouselItem.query.all(),
    render_navbar=RENDER_NAVBAR,
    render_carousel=RENDER_CAROUSEL,
    render_main_links=RENDER_MAIN_LINKS,
    render_footer=RENDER_FOOTER)

@app.route('/loghw/')
def loghw():
  seconds_since_epoch = time.time()
  current_datetime = dt.utcfromtimestamp(seconds_since_epoch - pst_offset)

  current_day_of_week = int(current_datetime.strftime("%w")) #1 is monday
  current_week_of_year = int(current_datetime.strftime("%W"))
  current_week_classes = getClassesFromWeek(current_week_of_year)

  # flash("It is {0} PST".format(current_datetime.strftime("%A, %B %d, %Y at %I:%M:%S %p")), category='info')
  flash("Beyond simple harmonic motion, the class information was copied from last year's schedule. Dr. Dann will have to update it to correspond to this year (e.g. correct days for HIWW, etc). Once he does, this warning message will disappear forever.",category='warning')

  return render_template('loghw.html',
    title='Class Log and HW',
    units=Unit.query.all(),
    classes=current_week_classes,
    day_of_week=current_day_of_week,
    render_navbar=RENDER_NAVBAR,
    render_current_week_schedule=RENDER_CURRENT_WEEK_SCHEDULE,
    render_scrollspy=RENDER_SCROLLSPY,
    render_footer=RENDER_FOOTER)

@app.route('/refreshJSON/')
def refreshJSON():
  global topics
  global times
  global carousel_images
  with open('app/static/json/topics.json') as f:
    newTopics = json.loads(f.read())
  with open('app/static/json/times.json') as f:
    newTimes = json.loads(f.read())
  with open('app/static/json/carousel_items.json') as f:
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

#FOR ADMIN USE ONLY
@app.route('/admin/')
def admin():
  return render_template('admin.html',
    title="Administrator",
    units=Unit.query.all(),
    classes=Class.query.all(),
    items=CarouselItem.query.all())

@app.route('/addClass/', methods=['GET', 'POST'])
def add_class():
  if request.method == 'GET': #GET method
    return "template for adding a class"
  else: #POST method
    return "Hello"

@app.route('/units/edit/<int:unit_id>/', methods=['GET', 'POST'])
def edit_unit(unit_id):
  #Make sure that the class we're looking at exists
  the_unit = Unit.query.get(unit_id)
  if the_unit == None: #If it doesn't exist...
    flash("There is no unit with an id of {0}".format(unit_id), category='error')
    return redirect(url_for('admin'))

  if request.method == 'GET': #GET method
    return render_template('edit_unit.html',
      u=the_unit,
      id=unit_id)

  else: #POST method
    ##TODO - Sanitize inputs
    f = request.form
    if 'title' in f:
      the_unit.title = f['title']
    if 'description' in f:
      the_unit.description = f['description']
    db.session.add(the_unit)
    db.session.commit()

    flash("Successfully updated Unit #{0}: {1}".format(unit_id, the_unit.title))
    return redirect(url_for('admin'))


@app.route('/classes/edit/<int:class_id>/', methods=['GET', 'POST'])
def edit_class(class_id):
  #Make sure that the class we're looking at exists
  the_class = Class.query.get(class_id)
  if the_class == None: #If it doesn't exist...
    flash("Class with id = {0} does not exist".format(class_id), category='error')
    return redirect(url_for('admin'))

  if request.method == 'GET': #GET method
    return render_template('edit_class.html',
      cl=the_class,
      id=class_id)
  else: #POST method
    #TODO - add validation here

    #There is a better way to do this, rather than clear all logs and then add them back
    the_class.clearItems()
    items = [request.form['log1'],request.form['log2'],request.form['log3'],request.form['log4'],request.form['log5'],request.form['log6']]
    for i in items:
      i = i.strip()
      if (i != ""):
        the_class.addItem(i)

    the_class.homework = request.form['homework']
    the_class.additional = request.form['additional']
    db.session.add(the_class)
    db.session.commit()

    flash("Successfully updated class #{0}".format(class_id))
    return redirect(url_for('admin'))

@app.route("/changeDates/", methods=['GET','POST'])
def changeDates():
  if request.method == 'GET': #GET method
    return render_template("changeDates.html")
  else: #POST method
    return "Hello"

#####################
#EDIT CAROUSEL ITEMS#
#####################

#As JSON
@app.route("/edit_carousel/", methods=['GET','POST'])
def edit_carousel():
  items = CarouselItem.query.all()
  #Build our JSON
  l = []
  for item in items:
    d = {}
    d['title'] = item.title
    d['description'] = item.description
    d['src'] = item.src
    d['alt'] = item.alt
    l.append(d)
  s = json.dumps(l)
  print s
  if request.method == 'GET': #GET method
    return render_template("edit_carousel.html",
      items=s)
  else: #POST method
    return "Posted yo"

#One Item
@app.route("/carousel_items/edit/<int:item_id>", methods=['GET','POST'])
def edit_carousel_item(item_id):
  #Make sure that the class we're looking at exists
  the_item = CarouselItem.query.get(item_id)
  if the_item == None: #If it doesn't exist...
    flash("Carousel item with id = {0} does not exist".format(item_id), category='error')
    return redirect(url_for('admin'))

  if request.method == 'GET': #GET method
    return render_template('edit_carousel_item.html',
      item=the_item,
      id=item_id)
  else: #POST method
    #TODO - add validation here
    f = request.form
    if 'title' in f:
      the_item.title = f['title']
    if 'description' in f:
      the_item.description = f['description']
    if 'src' in f:
      the_item.src = f['src']
    if 'alt' in f:
      the_item.alt = f['alt']
    db.session.add(the_item)
    db.session.commit()

    flash("Successfully updated Item #{0}: {1}".format(item_id, the_item.title))
    return redirect(url_for('admin'))

#Not the fastest, but it'll be fine
def getClassesFromWeek(weekNumber):
  all_classes = Class.query.all()
  week_classes = [None, None, None, None, None]
  for cl in all_classes:
    if cl.week_of_year == weekNumber:
      day = cl.day_of_week
      if day == 1: #Monday
        week_classes[0] = cl
      elif day == 2: #Tuesday
        week_classes[1] = cl
      elif day == 3: #Wednesday
        week_classes[2] = cl
      elif day == 4: #Thursday
        week_classes[3] = cl
      elif day == 5: #Friday
        week_classes[4] = cl
  return week_classes

#Handle Error Pages
@app.errorhandler(404) #404 = Page Not Found
def internal_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500) #500 = Internal server error
def internal_error(error):
    db.session.rollback() #Rollback the database in case a database error triggered the 500
    return render_template('500.html'), 500