'''
TODO
Form validation! I need to make sure Dr. Dann doesn't enter any weird html
Gotta make the rendering_options universal
Add visibility to unit model and add main link model
Add Hopskotch help to all admin pages
'''

#Import useful packages and objects
from flask import render_template, flash, redirect, url_for, request, Response
from functools import wraps
from app import app, db, bcrypt
from models import Unit, Class, CarouselItem, MainLink
from datetime import datetime as dt
import time
from calendar import timegm
import json

#Dictionary of valid username:hashed_password pairs
admins = {'jdann':'$2a$12$QI8bQfqc1Bscon9RjULyCu7umaBG4iLyghgC/0MnYkpADnXFaQen.'}

#8 hours, in seconds
pst_offset = 8 * 60 * 60

# with open('app/static/json/topics.json') as f:
#   topics = json.loads(f.read())

# with open('app/static/json/times.json') as f:
#   times = json.loads(f.read())

# with open('app/static/json/carousel_items.json') as f:
#   carousel_images = json.loads(f.read())

# #Seconds since epoch at which a new PST day w/ physics begins
# epoch_day_offsets = [timegm(time.strptime(t, "%m/%d/%y")) for t in times]

# #Zip time info into the topics dictionary
# try:
#   time_iter = iter(epoch_day_offsets)
#   for unit in topics:
#     for cl in unit['unit-classes']:
#       t = time_iter.next() #Seconds since epoch of a new UTC day - could throw an error
#       dt_obj = dt.utcfromtimestamp(t) #Datetime representing the local date and time
#       cl['time'] = t + pst_offset #Seconds since epoch of a new PST day
#       cl['dt-obj'] = dt_obj
#       cl['day-of-week'] = int(dt_obj.strftime("%w")) #1 = Monday, 2 = Tuesday, ..., 5 = Friday
#       cl['week-of-year'] = int(dt_obj.strftime("%W"))
# except Exception:
#   print "Oh no! We've encountered an error."
#   raise Exception("There are too many classes in the topics JSON file and not enough dates in the times JSON file. Ensure that there are at least as many dates as there are Physics classes.")

###############
#Authorization#
###############
def check_auth(username, password):
    #Checks to see if a username/password combination is valid
    for admin_username, pw_hash in admins.iteritems():
      if username == admin_username and bcrypt.check_password_hash(pw_hash, password):
        return True
    return False

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response("Error! Could not verify your access level for that URL. You have to login with proper credentials.",
    401, #Response code
    {'WWW-Authenticate': 'Basic realm="Login Required"'}) #Headers

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization #Have they validated previously?
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

#############
#MAIN ROUTES#
#############

@app.route('/')
@app.route('/index/')
def index():
  return render_template('index.html',
    title = 'Home',
    carousel_items=CarouselItem.query.all(),
    main_links=MainLink.query.all())

@app.route('/loghw/')
def loghw():
  seconds_since_epoch = time.time()
  current_datetime = dt.utcfromtimestamp(seconds_since_epoch - pst_offset)

  current_day_of_week = int(current_datetime.strftime("%w")) #1 is monday
  current_week_of_year = int(current_datetime.strftime("%W"))
  current_week_classes = getClassesFromWeek(current_week_of_year)

  flash("Beyond simple harmonic motion, the class information was copied from last year's schedule. Dr. Dann will have to update it to correspond to this year (e.g. correct days for HIWW, etc). Once he does, this warning message will disappear forever.",category='warning')

  return render_template('loghw.html',
    title='Class Log and HW',
    units=[u for u in Unit.query.all() if not u.isHidden()],
    classes=current_week_classes,
    day_of_week=current_day_of_week)

# @app.route('/refreshJSON/')
# def refreshJSON():
#   global topics
#   global times
#   global carousel_images
#   with open('app/static/json/topics.json') as f:
#     newTopics = json.loads(f.read())
#   with open('app/static/json/times.json') as f:
#     newTimes = json.loads(f.read())
#   with open('app/static/json/carousel_items.json') as f:
#     newImages = json.loads(f.read())
#   epoch_day_offsets = [timegm(time.strptime(t, "%m/%d/%y")) for t in newTimes]
#   try:
#     time_iter = iter(epoch_day_offsets)
#     for unit in newTopics:
#       for cl in unit['unit-classes']:
#         t = time_iter.next() #Seconds since epoch of a new UTC day - could throw an error
#         dt_obj = dt.utcfromtimestamp(t) #Datetime representing the local date and time
#         cl['time'] = t + pst_offset #Seconds since epoch of a new PST day
#         cl['dt-obj'] = dt_obj
#         cl['day-of-week'] = int(dt_obj.strftime("%w")) #1 = Monday, 2 = Tuesday, ..., 5 = Friday
#         cl['week-of-year'] = int(dt_obj.strftime("%W"))
#   except Exception:
#     flash("Oh no! There are too many classes in the topics JSON file and not enough dates in the times JSON file. Ensure that there are at least as many dates as there are Physics classes before trying again.", category='error')
#     return redirect(url_for('index'))
#   topics = newTopics
#   times = newTimes
#   carousel_images = newImages
#   flash('JSON files successfully updated')
#   return redirect(url_for('index'))

################
#ADMINISTRATIVE#
################

@app.route('/admin/')
@requires_auth
def admin():
  return render_template('admin.html',
    title="Administrator",
    units=Unit.query.all(),
    classes=Class.query.all(),
    items=CarouselItem.query.all(),
    main_links=MainLink.query.all())

############
#Edit Units#
############

#Edit a particular unit
@app.route('/units/edit/<int:unit_id>/', methods=['GET', 'POST'])
@requires_auth
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

#Edit all units as JSON
@app.route('/edit_units/', methods=['GET', 'POST'])
@requires_auth
def edit_units():
  if request.method == 'GET': #GET method
    return render_template('edit_units.html')
  else: #POST method
    return "Posted"

#Assign classes to various units
@app.route('/assign_classes/', methods=['GET', 'POST'])
@requires_auth
def assign_classes():
  if request.method == 'GET': #GET method
    return render_template('assign_classes.html')
  else: #POST method
    return "Posted"

##############
#Edit Classes#
##############

#Edit a particular class
@app.route('/classes/edit/<int:class_id>/', methods=['GET', 'POST'])
@requires_auth
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

#Edit all classes as JSON
@app.route('/edit_classes/', methods=['GET','POST'])
@requires_auth
def edit_classes():
  if request.method == 'GET': #GET method
    return render_template('edit_classes.html',
      classes=Class.query.all())
  else: #POST method
    return "Posted"


#Change the dates associated with the classes
@app.route("/change_dates/", methods=['GET','POST'])
@requires_auth
def change_dates():
  if request.method == 'GET': #GET method
    return render_template("change_dates.html",
      classes=Class.query.all())
  else: #POST method
    return "Hello"

#####################
#Edit Carousel Items#
#####################

#Edit one particular carousel item
@app.route("/carousel_items/edit/<int:item_id>", methods=['GET','POST'])
@requires_auth
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

#Edit all carousel items as JSON
@app.route("/edit_carousel/", methods=['GET','POST'])
@requires_auth
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
  s = json.dumps(l, sort_keys=True, indent=4)
  print s
  if request.method == 'GET': #GET method
    return render_template("edit_carousel.html",
      items=s)
  else: #POST method
    return "Posted yo"

#################
#EDIT MAIN LINKS#
#################
@app.route('/edit_main_links/')
def edit_main_links():
  return "Hello"


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

################
#ERROR HANDLERS#
################

@app.errorhandler(404) #404 = Page Not Found
def internal_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500) #500 = Internal server error
def internal_error(error):
    db.session.rollback() #Rollback the database in case a database error triggered the 500
    return render_template('500.html'), 500