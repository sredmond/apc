'''
HTML is only at main link text, class log, hw, and additional

TODO
Big JSON editor
Verify MainLink content
Revamp Class edit
Resource files
(Modify rendering options?)

TODO
Form validation! I need to make sure Dr. Dann doesn't enter any weird html
Add visibility to unit model edit (?) and add main link model
Add Hopskotch help to all admin pages

Verify main link content

Visual
Carousel Item
  Angular preview
  Force image to be a certain size
'''

#Import useful packages and objects
from flask import render_template, flash, redirect, url_for, request, session, Response
from functools import wraps
from app import app, db, bcrypt
from models import Unit, Class, CarouselItem, MainLink
from datetime import datetime as dt
import time
from calendar import timegm
import json

#Dictionary of valid username:hashed_password pairs (using bcrypt)
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
        session['authorized'] = True
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
        if not auth or not check_auth(auth.username, auth.password) or not session.get('authorized'):
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
    units=[u for u in Unit.query.all() if u.isVisible()],
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

@app.route('/tests/')
def tests():
  return render_template('tests.html',
    title="Old AP Tests and Solutions")

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

####################
#Edit All (as JSON)#
####################
#A full reassignment of the content of the website
@app.route('/edit/', methods=['GET','POST'])
@requires_auth
def edit():
  if request.method == 'GET':
    unit_models = Unit.query.all();
    class_models=Class.query.all();
    carousel_item_models=CarouselItem.query.all();
    main_link_models=MainLink.query.all();
    
    #Construct all the JSON maps
    content=[unit_model.toJSON() for unit_model in unit_models]
    dates=[class_model.pst_datetime.strftime('%m/%d/%y') for class_model in class_models]
    carousel_items = [carousel_item_model.toJSON() for carousel_item_model in carousel_item_models]
    main_links = [main_link_model.toJSON() for main_link_model in main_link_models]

    return render_template('edit.html',
      content=formatJSON(content),
      carousel_items=formatJSON(carousel_items),
      main_links=formatJSON(main_links),
      dates=formatJSON(dates),
      title="Edit JSON")
  else: #POST method
    # try: #Todo - better error catching
      data = json.loads(request.form['all'])

      # for key, value in data.iteritems():
      #   print key, value
      content, dates, carousel_items, main_links = data['content'], data['dates'], data['carousel_items'], data['main_links']
      print content, dates, carousel_items, main_links
      #Seconds since epoch at which a new PST day w/ physics begins
      epoch_day_offsets = [timegm(time.strptime(t, "%m/%d/%y")) for t in dates]
      
      #Zip time info into the topics dictionary
      date_iter = iter(epoch_day_offsets)

      new_units = []
      #Populate the topics into their respective units, with the dates loaded in too
      for unit in content:
        unit_model = Unit()
        unit_model.title=unit['title']
        unit_model.description=unit['description']
        unit_model.visible = unit['visible']
        for cl in unit['classes']:
          class_model = Class() #Make an empty model

          #Fill it with topical values
          for item in cl['items']:
            class_model.addItem(item)
          class_model.homework=cl['homework']
          if 'additional' in cl:
            class_model.additional = cl['additional']

          #Fill it with time values (could mess up here)
          t = date_iter.next() #Seconds since epoch of a new UTC day - could throw an error
          pst_dt = dt.utcfromtimestamp(t) #Datetime representing the local date and time
          class_model.epoch_time = t + pst_offset #Seconds since epoch of a new PST day
          class_model.pst_datetime = pst_dt
          class_model.day_of_week = int(pst_dt.strftime("%w")) #1 = Monday, 2 = Tuesday, ..., 5 = Friday
          class_model.week_of_year = int(pst_dt.strftime("%W"))

          unit_model.addClass(class_model)
        new_units.append(unit_model)

      new_carousel_items = []
      #Add carousel items
      for item in carousel_items:
        new_item = CarouselItem()
        if 'title' in item:
          new_item.title=item['title']
        if 'description' in item:
          new_item.description=item['description']
        if 'src' in item:
          new_item.src=item['src']
        if 'alt' in item:
          new_item.alt=item['alt']
        new_carousel_items.append(new_item)


      new_main_links = []
      for link in main_links:
        new_link = MainLink()
        if 'link' in link:
          new_link.link = link['link']
        if 'media-type' in link:
          new_link.media_type = link['media-type']
        new_main_links.append(new_link);

      #Now that we have all the models, clear the database and push all the new values on
      Unit.query.delete()
      Class.query.delete()
      CarouselItem.query.delete()
      MainLink.query.delete()

      for unit_model in new_units:
        db.session.add(unit_model)
      for carousel_item_model in new_carousel_items:
        db.session.add(carousel_item_model)
      for main_link_model in new_main_links:
        db.session.add(main_link_model)
      db.session.commit()
      flash('Successfully updated database to reflect changes')
    # # except Exception as e:
    #   print "Error: " + repr(e)
    #   flash('Uncaught Exception: {0}'.format(e), category='error')
      return redirect(url_for('admin'))

@app.route('/getAll/', methods=['GET'])
def getAll():
  unit_models = Unit.query.all();
  class_models=Class.query.all();
  carousel_item_models=CarouselItem.query.all();
  main_link_models=MainLink.query.all();
  
  #Construct all the JSON maps
  content=[unit_model.toJSON() for unit_model in unit_models]
  dates=[class_model.pst_datetime.strftime('%m/%d/%y') for class_model in class_models]
  carousel_items = [carousel_item_model.toJSON() for carousel_item_model in carousel_item_models]
  main_links = [main_link_model.toJSON() for main_link_model in main_link_models]

  out = {}
  out['content']=content
  out['carousel_items']=carousel_items
  out['main_links']=main_links
  out['dates']=dates
  return json.dumps(out)

@app.route('/help/')
def help():
  return render_template('help.html',
    title="Help")

##############
#UPLOAD FILES#
##############
@app.route('/upload/', methods=['GET'])
def upload():
  return render_template('upload.html')


@app.route('/+upload/', methods=['GET', 'POST'])
def uploadAux():
  print request
  print request.files
  if request.method == 'GET':
      # we are expected to return a list of dicts with infos about the already available files:
      file_infos = []
      for file_name in list_files():
          file_url = url_for('download', file_name=file_name)
          file_size = get_file_size(file_name)
          file_infos.append(dict(name=file_name,
                                 size=file_size,
                                 url=file_url))
      return jsonify(files=file_infos)

  if request.method == 'POST':
      # we are expected to save the uploaded file and return some infos about it:
      #                              vvvvvvvvv   this is the name for input type=file
      data_file = request.files.get('data_files')
      file_name = data_file.filename
      save_file(data_file, file_name)
      file_size = get_file_size(file_name)
      file_url = url_for('download', file_name=file_name)
      # providing the thumbnail url is optional
      thumbnail_url = url_for('thumbnail', file_name=file_name)
      return jsonify(name=file_name,
                     size=file_size,
                     url=file_url,
                     thumbnail=thumbnail_url)

############
#Edit Units#
############

#Edit a particular unit
@app.route('/units/edit/<int:unit_id>/', methods=['GET', 'POST'])
@requires_auth
def edit_unit(unit_id):
  
  #Make sure that the unit we're looking at exists
  the_unit = Unit.query.get(unit_id)
  if the_unit == None: #If it doesn't exist...
    flash("Unit with ID={0} does not exist...".format(unit_id), category='error')
    return redirect(url_for('admin'))

  if request.method == 'GET': #GET method
    return render_template('edit_unit.html',
      u=the_unit,
      id=unit_id)

  else: #POST method
    f = request.form
    if 'title' in f:
      the_unit.title = f['title']
    else:
      flash("Units must have an associatied title", category='error')
      return redirect(url_for('admin'))
    if 'description' in f:
      the_unit.description = f['description']
    else:
      flash("Units must have an associatied description", category='error')
      return redirect(url_for('admin'))
    db.session.add(the_unit)
    db.session.commit()

    flash("Successfully updated Unit #{0}: {1}".format(unit_id, the_unit.title), category='message')
    return redirect(url_for('admin'))

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
    flash("Class with ID={0} does not exist...".format(class_id), category='error')
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
    classes = Class.query.all()
    s = []
    for cl in classes:
      s.append(str(cl.pst_datetime))
    return render_template("change_dates.html",
      text='\n'.join(s))
  else: #POST method
    return "Hello"

#####################
#Edit Carousel Items#
#####################

#Edit one particular carousel item
@app.route("/carousel_items/edit/<int:item_id>", methods=['GET','POST'])
@requires_auth
def edit_carousel_item(item_id):
  #Make sure that the item we're looking at exists
  the_item = CarouselItem.query.get(item_id)
  if the_item == None: #If it doesn't exist...
    flash("Carousel Item with ID={0} does not exist...".format(item_id), category='error')
    return redirect(url_for('admin'))
  if request.method == 'GET': #GET method
    return render_template('edit_carousel_item.html',
      item=the_item,
      id=item_id)
  else: #POST method
    f = request.form
    if 'title' in f:
      #It's totally fine to have HTML entities in the title. Jinja2 will escape them
      the_item.title = f['title']
    else:
      flash("Carousel items must have an associated title.", category='error')
      return redirect(url_for('admin'))
    if 'description' in f:
      the_item.description = f['description']
    else:
      flash("Carousel items must have an associated description.", category='error')
      return redirect(url_for('admin'))
    if 'src' in f:
      the_item.src = f['src']
    else:
      flash("Carousel items must have an associated source.", category='error')
      return redirect(url_for('admin'))
    if 'alt' in f:
      the_item.alt = f['alt']
    db.session.add(the_item)
    db.session.commit()

    flash("Successfully updated Item #{0}: {1}".format(item_id, the_item.title), category='message')
    return redirect(url_for('admin'))

#################
#EDIT MAIN LINKS#
#################
@app.route('/main_links/edit/<int:link_id>', methods=['GET','POST'])
def edit_main_link(link_id):
  #Make sure that the link we're looking at exists
  the_link = MainLink.query.get(link_id)
  if the_link == None: #If it doesn't exist...
    flash("Main Link with ID={0} does not exist...".format(link_id), category='error')
    return redirect(url_for('admin'))

  if request.method == 'GET': #GET method
    return render_template('edit_main_link.html',
      l=the_link,
      id=link_id)

  else: #POST method
    f = request.form
    if 'link' in f:
      the_unit.title = f['link']
    else:
      flash("Main Links must have an associatied link text", category='error')
      return redirect(url_for('admin'))
    if 'media-type' in f:
      the_unit.description = f['media-type']
    else:
      flash("Main Links must have an associated media type", category='error')
      return redirect(url_for('admin'))
    db.session.add(the_link)
    db.session.commit()

    flash("Successfully updated Main Link #{0}: {1}".format(link_id, the_unit.title), category='message')
    return redirect(url_for('admin'))

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

###################
#UTILITY FUNCTIONS#
###################

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

def filterClasses(filterText):
  classes = Class.query.all()
  matching_classes = []
  for cl in classes:
    for item in cl.getItems():
      if filterText in item:
        matching_classes.append(cl)
        break
  print matching_classes

def formatJSON(validJSON):
  return json.dumps(validJSON, sort_keys=True, indent=2, separators=(',', ': '))

def noHTMLEntities(str):
  return str.find('<') == -1 and str.find('>') == -1 and str.find('"') == -1 and str.find('\'') == -1 and str.find('&') == -1