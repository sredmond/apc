#!/usr/bin/env python
""" Import all static information into the database
JSON files are stored at /app/static/json/
"""
import time
from datetime import datetime
from calendar import timegm
import json

from app import db
from app.models import Unit, Lesson, CarouselItem, Reference

pst_offset = 8 * 60 * 60

raw_input("> Warning! This action will erase the old database.\nEnter CTRL-C to abort, or any other key to proceed: ")

# Wipe the old database
Unit.query.delete()
Lesson.query.delete()
CarouselItem.query.delete()
Reference.query.delete()
db.session.commit()

# Load the JSON information
with open('app/static/json/content.json') as f:
    content = json.loads(f.read())

with open('app/static/json/dates.json') as f:
    dates = json.loads(f.read())

with open('app/static/json/carousel.json') as f:
    carousel = json.loads(f.read())

with open('app/static/json/references.json') as f:
    references = json.loads(f.read())

# Seconds since epoch at which a new PST day w/ physics begins
epoch_day_offsets = [timegm(time.strptime(date, "%m/%d/%y")) for date in dates]

# Used to iterate through our potential times
time_iter = iter(epoch_day_offsets)

# Populate the lessons into their respective units, including dates
for unit in content:
    unit_model = Unit()
    unit_model.title = unit.get('title')
    unit_model.description = unit.get('description')
    for lesson in unit['lessons']:
        lesson_model = Lesson()
        for item in lesson['items']:
            lesson_model.addItem(item)
        lesson_model.homework=lesson.get('homework')
        lesson_model.additional = lesson.get('additional')

        # Add time values
        t = time_iter.next() # Seconds since epoch of a new UTC day - could throw an error
        pst_dt = datetime.utcfromtimestamp(t) # Datetime representing the local date and time
        lesson_model.epoch_time = t + pst_offset # Seconds since epoch of a new PST day
        lesson_model.pst_datetime = pst_dt
        lesson_model.day_of_week = int(pst_dt.strftime("%w")) # 1 = Monday, 2 = Tuesday, ..., 5 = Friday
        lesson_model.week_of_year = int(pst_dt.strftime("%W"))

        unit_model.addLesson(lesson_model)
    unit_model.visible = True
    db.session.add(unit_model)
db.session.commit()

# Populate the carousel
for item in carousel:
    carousel_model = CarouselItem()
    carousel_model.title = item.get('title')
    carousel_model.description = item.get('description')
    carousel_model.src = item.get('src')
    carousel_model.alt = item.get('alt')
    db.session.add(carousel_model)
db.session.commit()

# Populate the references
for ref in references:
    reference_model = Reference()
    reference_model.href = ref.get('href')
    reference_model.title = ref.get('title')
    reference_model.media_type = ref.get('media-type')
    db.session.add(reference_model);
db.session.commit()