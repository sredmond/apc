from app import db
import bcrypt
ROLE_USER = 0
ROLE_ADMIN = 1

unit_title_default = "Unit Title"
unit_description_default = "Unit Description"
class_homework_default = "Homework: TBD"
max_string_length = 65535
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
    
#     #Information for logging in 
#     email = db.Column(db.String(120), unique = True)
#     hashed_password = db.Column(db.String(60));

#     #Personal Information
#     first_name = db.Column(db.String(20))
#     last_name = db.Column(db.String(20))
#     grade = db.Column(db.SmallInteger)
    
#     #Timing
#     created = db.Column(db.DateTime)
#     last_logged_in = db.Column(db.DateTime)

#     #Administrative
#     role = db.Column(db.SmallInteger, default = ROLE_USER)
    
#     #Necessary methods for Flask-Login
#     def is_authenticated(self):
#         return True

#     def is_active(self):
#         return True

#     def is_anonymous(self):
#         return False

#     def get_id(self):
#         return unicode(self.id)

#     def verify_password(self, password):
#       return bcrypt.hashpw(password, self.hashed_password) == self.hashed_password

#     def __repr__(self):
#         return '<User %r>' % (self.email)

class Unit(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  title = db.Column(db.String(40), default=unit_title_default)
  description = db.Column(db.String(120), default=unit_description_default)
  classes = db.relationship('Class', backref = 'unit', lazy = 'dynamic')

  def addClass(self, newClass):
    if not self.hasClass(newClass):
      self.classes.append(newClass);

  def removeClass(self, oldClass):
    if self.hasClass(oldClass):
      self.classes.remove(oldClass)

  def hasClass(self, aClass):
    return aClass in self.classes
  
  def __repr__(self):
    return '<Unit %r>' % (self.title)

class Class(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))

  #Agenda Items
  item_0 = db.Column(db.String(max_string_length), default="")
  item_1 = db.Column(db.String(max_string_length), default="")
  item_2 = db.Column(db.String(max_string_length), default="")
  item_3 = db.Column(db.String(max_string_length), default="")
  item_4 = db.Column(db.String(max_string_length), default="")
  item_5 = db.Column(db.String(max_string_length), default="")
  numItems = 0;

  homework = db.Column(db.String(max_string_length), default=class_homework_default)
  additional = db.Column(db.String(max_string_length), default="None")

  #Time fields
  epoch_time = db.Column(db.Integer) #Seconds since the epoch of a new PST day
  pst_datetime = db.Column(db.DateTime)
  day_of_week = db.Column(db.SmallInteger) #1 = Monday, 2 = Tuesday, ..., 5 = Friday
  week_of_year = db.Column(db.SmallInteger) #0 = first week, 52 = last week

  def addItem(self, new_item):
    if 0 <= self.numItems < 6:
      if self.numItems == 0:
        self.item_0 = new_item
      elif self.numItems == 1:
        self.item_1 = new_item
      elif self.numItems == 2:
        self.item_2 = new_item
      elif self.numItems == 3:
        self.item_3 = new_item
      elif self.numItems == 4:
        self.item_4 = new_item
      elif self.numItems == 5:
        self.item_5 = new_item
      self.numItems += 1
      return True
    return False

  def removeItem(self):
    if 0 < self.numItems <= 6:
      if self.numItems == 1:
        self.item_0 = ""
      elif self.numItems == 2:
        self.item_1 = ""
      elif self.numItems == 3:
        self.item_2 = ""
      elif self.numItems == 4:
        self.item_3 = ""
      elif self.numItems == 5:
        self.item_4 = ""
      elif self.numItems == 6:
        self.item_5 = ""
      self.numItems -= 1
      return True
    return False

  def clearItems(self):
    self.item_0 = ""
    self.item_1 = ""
    self.item_2 = ""
    self.item_3 = ""
    self.item_4 = ""
    self.item_5 = ""

  def getItems(self):
    return [self.item_0, self.item_1, self.item_2, self.item_3, self.item_4, self.item_5]

  # def setItems(self, items): #Relatively slow, but it won't be called that much anyway
  #   self.clearItems()
  #   for i in items:
  #     self.addItem(i)
  
  def __repr__(self):
    return '<Class: %r>' % (self.homework)

class CarouselItem(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  title = db.Column(db.String(max_string_length), default="")
  description = db.Column(db.String(max_string_length), default="")
  src = db.Column(db.String(max_string_length), default="")
  alt = db.Column(db.String(max_string_length), default="")

  def __repr__(self):
    return '<Carousel Item: %r>' % (self.title)


