#!venv/bin/python

#Let's assume all JSON files are perfectly formatted, shall we?
# (this also means we have more times than class periods)

#For migrating from .json files to our database
from app import db
from app.models import Unit, Class, CarouselItem, MainLink
import json
from datetime import datetime as dt
from calendar import timegm
import time
pst_offset = 8 * 60 * 60
with open('app/static/json/topics.json') as f:
  topics = json.loads(f.read())

with open('app/static/json/times.json') as f:
  times = json.loads(f.read())

#Seconds since epoch at which a new PST day w/ physics begins
epoch_day_offsets = [timegm(time.strptime(t, "%m/%d/%y")) for t in times]
#Zip time info into the topics dictionary
time_iter = iter(epoch_day_offsets)

#Populate the topics into their respective units, with the dates loaded in too
for unit in topics:
	unit_model = Unit()
	unit_model.title=unit['unit-title']
	unit_model.description=unit['unit-description']
	for cl in unit['unit-classes']:
		class_model = Class() #Make an empty model

		#Fill it with topical values
		for item in cl['class-log']:
			class_model.addItem(item)
		class_model.homework=cl['homework']
		if 'additional' in cl:
			class_model.additional = cl['additional']

		#Fill it with time values (could mess up here)
		t = time_iter.next() #Seconds since epoch of a new UTC day - could throw an error
		pst_dt = dt.utcfromtimestamp(t) #Datetime representing the local date and time
		class_model.epoch_time = t + pst_offset #Seconds since epoch of a new PST day
		class_model.pst_datetime = pst_dt
		class_model.day_of_week = int(pst_dt.strftime("%w")) #1 = Monday, 2 = Tuesday, ..., 5 = Friday
		class_model.week_of_year = int(pst_dt.strftime("%W"))

		unit_model.addClass(class_model)
	unit_model.hidden = False
	db.session.add(unit_model)
db.session.commit()

#Populate the carousel items
with open('app/static/json/carousel_items.json') as f:
  items = json.loads(f.read())

for item in items:
  new_item = CarouselItem()
  if 'title' in item:
  	new_item.title=item['title']
  if 'description' in item:
  	new_item.description=item['description']
  if 'src' in item:
  	new_item.src=item['src']
  if 'alt' in item:
  	new_item.alt=item['alt']
  db.session.add(new_item)
db.session.commit()

#Populate the main links
with open('app/static/json/main_links.json') as f:
	links = json.loads(f.read())

for link in links:
	new_link = MainLink()
	if 'link' in link:
		new_link.link = link['link']
	if 'media-type' in link:
		new_link.media_type = link['media-type']
	db.session.add(new_link);
db.session.commit()