from app import db
import bcrypt
ROLE_USER = 0
ROLE_ADMIN = 1

defaults = {
    'unit_title': 'Unit Title',
    'unit_description': 'Unit Description',
    'lesson_homework': 'TBD'
}
max_string_length = 1000


class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(max_string_length),
        default=defaults['unit_title'])
    description = db.Column(db.String(max_string_length),
        default=defaults['unit_description'])
    lessons = db.relationship('Lesson', backref='unit', lazy='dynamic')
    visible = db.Column(db.Boolean, default=True)

    def add_lesson(self, newLesson):
        if not self.has_lesson(newLesson):
            self.lessons.append(newLesson)

    def remove_lesson(self, oldLesson):
        if self.has_lesson(oldLesson):
            self.lessons.remove(oldLesson)

    def has_lesson(self, someLesson):
        return someLesson in self.lessons

    def to_json(self):
        return {'title': self.title,
                'description': self.description,
                'visible': self.visible,
                'lessons': [lesson.to_json() for lesson in self.lessons]}

    def __repr__(self):
        return '<Unit %r>' % self.title


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))

    # Agenda Items
    item_0 = db.Column(db.String(max_string_length), default="")
    item_1 = db.Column(db.String(max_string_length), default="")
    item_2 = db.Column(db.String(max_string_length), default="")
    item_3 = db.Column(db.String(max_string_length), default="")
    item_4 = db.Column(db.String(max_string_length), default="")
    item_5 = db.Column(db.String(max_string_length), default="")
    numItems = 0

    homework = db.Column(db.String(max_string_length),
        default=defaults['lesson_homework'])
    additional = db.Column(db.String(max_string_length),
        default="None")

    # Time fields
    epoch_time = db.Column(db.Integer)  # Seconds since epoch of a PST day
    pst_datetime = db.Column(db.DateTime)
    day_of_week = db.Column(db.SmallInteger)  # 1=Monday, 2=Tuesday, 5=Friday
    week_of_year = db.Column(db.SmallInteger)  # 0=1st week, 52=last week

    def add_item(self, new_item):
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

    def remove_item(self):
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

    def clear_items(self):
        self.item_0 = ""
        self.item_1 = ""
        self.item_2 = ""
        self.item_3 = ""
        self.item_4 = ""
        self.item_5 = ""

    def get_items(self):
        return self.get_all_items()[:self.numItems]

    def get_all_items(self):
        return [self.item_0, self.item_1, self.item_2,
                self.item_3, self.item_4, self.item_5]

    def to_json(self):
        return {'items': [item for item in self.get_items() if len(item) > 0],
                'homework': self.homework,
                'additional': self.additional}

    def __repr__(self):
        return '<Lesson: %r>' % self.homework


class CarouselItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(max_string_length), default="")
    description = db.Column(db.String(max_string_length), default="")
    src = db.Column(db.String(max_string_length), default="")
    alt = db.Column(db.String(max_string_length), default="")

    def to_json(self):
        return {'title': self.title,
                'description': self.description,
                'src': self.src,
                'alt': self.alt}

    def __repr__(self):
        return '<Carousel Item: %r>' % self.title


class Reference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    href = db.Column(db.String(max_string_length), default="")
    title = db.Column(db.String(max_string_length), default="")
    media_type = db.Column(db.String(max_string_length), default="")

    def to_json(self):
        return {'href': self.href,
                'title': self.title,
                'media_type': self.media_type}

    def __repr__(self):
        return '<Reference: %r>' % self.title
