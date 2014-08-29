'''
HTML is only at main link text, class log, hw, and additional

TODO
Verify MainLink content
Resource files
(Modify rendering options?)

TODO
Form validation! I need to make sure Dr. Dann doesn't enter any weird html

Verify main link content

Visual
Carousel Item
  Angular preview
  Force image to be a certain size
'''

#Import useful packages and objects
from flask import render_template, flash, redirect, url_for, request, session, Response
from functools import wraps
from datetime import datetime as dt
from calendar import timegm
import time
import json
from os import listdir
import os.path

from app import app, db, bcrypt
from models import Unit, Lesson, CarouselItem, Reference
from config import basedir, ADMIN_USERNAME, ADMIN_PASSWORD

#8 hours, in seconds
PST_OFFSET = 8 * 60 * 60

# #############
# Authorization
# #############
def check_auth(username, password):
    """Checks to see if a username/password combination is valid"""
    if username == ADMIN_USERNAME and bcrypt.check_password_hash(ADMIN_PASSWORD, password):
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

# ##################
# APPLICATION ROUTES
# ##################

@app.route('/')
@app.route('/index/')
def index():
  return render_template('app/index.html',
    title = 'Home',
    carousel_items=CarouselItem.query.all(),
    references=Reference.query.all())

@app.route('/loghw/')
def loghw():
  seconds_since_epoch = time.time()
  current_datetime = dt.utcfromtimestamp(seconds_since_epoch - PST_OFFSET)

  current_day_of_week = int(current_datetime.strftime("%w")) #1 is monday
  current_week_of_year = int(current_datetime.strftime("%W"))
  current_lessons = get_lessons_from_week(current_week_of_year)

  # flash("Beyond simple harmonic motion, the class information was copied from last year's schedule. Dr. Dann will have to update it to correspond to this year (e.g. correct days for HIWW, etc). Once he does, this warning message will disappear forever.",category='warning')

  return render_template('app/loghw.html',
    title='Class Log and HW',
    units=Unit.query.filter(Unit.visible).all(),
    lessons=current_lessons,
    day_of_week=current_day_of_week)

# ##############
# ADMINISTRATIVE
# ##############

@app.route('/admin/')
@requires_auth
def admin():
  return render_template('admin/admin.html',
    title="Administrator",
    units=Unit.query.all(),
    lessons=Lesson.query.all(),
    items=CarouselItem.query.all(),
    references=Reference.query.all())

# Edit the database as JSON
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
          class_model.epoch_time = t + PST_OFFSET #Seconds since epoch of a new PST day
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
  return render_template('admin/help.html',
    title="Help")

# ############
# Upload Files
# ############
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

# ###########################
# Edit/Update Model Instances
# ###########################

# Edit a particular Unit
@app.route('/units/edit/<int:unit_id>/', methods=['GET', 'POST'])
@requires_auth
def edit_unit(unit_id):
  # Does this unit exist?
  unit = Unit.query.get(unit_id)
  if not unit:
    flash("Unit with ID of `{0}` does not exist.".format(unit_id), category='error')
    return redirect(url_for('admin'))

  # Edit
  if request.method == 'GET':
    return render_template('admin/edit_unit.html',
      unit=unit)
  # Update
  else:
    f = request.form
    if 'title' not in f or 'description' not in f or 'media-type' not in f:
      flash("A Unit must contain a title and description. Did not update Unit {0}".format(unit_id), category='error')
      return redirect(url_for('admin'))
    unit.title = f['title']
    unit.description = f['description']
    db.session.add(unit)
    db.session.commit()

    flash("Successfully updated Unit #{0}: {1}".format(unit_id, unit.title), category='message')
    return redirect(url_for('admin'))

# Edit a particular Lesson
@app.route('/lessons/edit/<int:lesson_id>/', methods=['GET', 'POST'])
@requires_auth
def edit_lesson(lesson_id):
  # Does this lesson exist?
  lesson = Lesson.query.get(lesson_id)
  if not lesson:
    flash("A Lesson with ID of `{0}` does not exist.".format(lesson_id), category='error')
    return redirect(url_for('admin'))

  # Edit
  if request.method == 'GET': 
    return render_template('admin/edit_lesson.html',
      lesson=lesson)
  # Update
  else:
    # All fields can contain HTML, so we need to validate here.
    # TODO More efficient method
    f = request.form
    lesson.clearItems()
    items = [f['log1'],f['log2'],f['log3'],f['log4'],f['log5'],f['log6']]
    for i in items:
      i = i.strip()
      # TODO Additional validation
      if i != "":
        lesson.addItem(i)

    lesson.homework = request.form['homework'] # TODO Additional validation
    lesson.additional = request.form['additional'] # TODO Additional validation
    db.session.add(lesson)
    db.session.commit()

    flash("Successfully updated Lesson #{0}".format(class_id))
    return redirect(url_for('admin'))

# Edit a particular CarouselItem
@app.route("/carousel/edit/<int:item_id>", methods=['GET','POST'])
@requires_auth
def edit_carousel(item_id):
  # Does this carousel item exist?
  item = CarouselItem.query.get(item_id)
  if not item:
    flash("Carousel Item with ID of `{0}` does not exist.".format(item_id), category='error')
    return redirect(url_for('admin'))
  
  # Edit
  if request.method == 'GET': #GET method
    return render_template('edit_carousel_item.html',
      item=item)
  # Update
  else:
    f = request.form
    if 'title' not in f or 'description' not in f or 'src' not in f:
      flash("A Carousel Item must contain a title, description, and src. Did not update Carousel Item {0}".format(item_id), category='error')
      return redirect(url_for('admin'))
    
    item.title = f['title']
    item.description = f['description']
    item.src = f['src']
    item.alt = f.get('alt')  # Could be None
    db.session.add(item)
    db.session.commit()

    flash("Successfully updated Carousel Item #{0}: {1}".format(item_id, item.title), category='message')
    return redirect(url_for('admin'))

# Edit a particular Reference
@app.route('/references/edit/<int:reference_id>', methods=['GET','POST'])
def edit_reference(reference_id):
  #Does this reference exist?
  ref = Reference.query.get(reference_id)
  if not ref:
    flash("Reference with ID of `{0}` does not exist.".format(reference_id), category='error')
    return redirect(url_for('admin'))

  # Edit
  if request.method == 'GET':
    return render_template('admin/edit_reference.html',
      ref=ref)
  # Update
  else:
    f = request.form
    if 'title' not in f or 'href' not in f or 'media-type' not in f:
      flash("References must contain a title, href, and media-type. Did not update Reference {0}".format(reference_id), category='error')
      return redirect(url_for('admin'))
    ref.title = f['title']
    ref.href = f['href']  # TODO Check for bad things here
    ref.media_type = f['media-type']
    db.session.add(ref)
    db.session.commit()

    flash("Updated Reference #{0}: `{1}` ({2}) linked to `{3}`".format(reference_id, ref.title, ref.media_type, ref.href), category='message')
    return redirect(url_for('admin'))

# ##############
# ERROR HANDLERS
# ##############
@app.errorhandler(404)  # 404 = Page Not Found
def internal_error(error):
    return render_template('static/404.html'), 404

@app.errorhandler(500)  # 500 = Internal server error
def internal_error(error):
    db.session.rollback()  # Rollback the database in case a database error triggered the 500
    return render_template('static/500.html'), 500

# #############
# MISCELLANEOUS
# #############
@app.route('/tests/')
def tests():
  # TODO better test organization
  tests_path = os.path.join(basedir, 'app/static/resources/tests/')
  all_tests = {}
  for subdir in os.listdir(tests_path):
    tests = {}
    test_files = os.listdir(os.path.join(tests_path, subdir))
    if 'mech_questions.pdf' in tests:
      tests['MQ'] = 'app/static/resources/tests/{0}/mech_questions.pdf'.format(subdir)
    if 'em_questions.pdf' in tests:
      tests['EMQ'] = 'app/static/resources/tests/{0}/em_questions.pdf'.format(subdir)
    if 'mech_solutions.pdf' in tests:
      tests['MS'] = 'app/static/resources/tests/{0}/mech_solutions.pdf'.format(subdir)
    if 'em_solutions.pdf' in tests:
      tests['EMS'] = 'app/static/resources/tests/{0}/em_solutions.pdf'.format(subdir)
    all_tests[subdir] = tests
  return render_template('static/tests.html',
    title="Old AP Tests and Solutions",
    tests=all_tests)

# #################
# UTILITY FUNCTIONS
# #################

#Not the fastest, but it'll be fine
def get_lessons_from_week(weekNumber):
  lessons = Lesson.query.all()
  current_lessons = [None, None, None, None, None]
  for lesson in lessons:
    if lesson.week_of_year == weekNumber:
      day = lesson.day_of_week
      if day == 1: #Monday
        current_lessons[0] = lesson
      elif day == 2: #Tuesday
        current_lessons[1] = lesson
      elif day == 3: #Wednesday
        current_lessons[2] = lesson
      elif day == 4: #Thursday
        current_lessons[3] = lesson
      elif day == 5: #Friday
        current_lessons[4] = lesson
  return current_lessons

def formatJSON(validJSON):
  return json.dumps(validJSON, sort_keys=True, indent=2, separators=(',', ': '))
