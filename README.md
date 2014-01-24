apc
===

A redesign of Menlo's AP Physics C website written using Python's Flask microframework and Jinja2's templating engine. Built on Bootstrap's core framework, this site delivers key information to Menlo students. Class information is stored in JSON files (/app/static/json/topics.json and /app/static/json/times.json). The information is separated into class content (topics), and class schedule/timing (times) for ease of use and cross-year compatibility. The home page features a carousel of Physics-related images and a table of relevant links. The images are also stored in a carouselImages.json file, but those need not be changed too vigorously.

Display
-------
The bulk of the website is displayed on the Class Log and Homework page (/loghw endpoint). When a request is made, the server intelligently determines which of the many Physics classes are taking place in the current week. It then renders these classes emphatically (using Bootstrap's tabs), and highlights the current day's information. The rest of the Physics class information is displayed linearly, with collapsibles and a scrollspy accelerating and easing navigation. Moment.js allows the scrollspy to calculate dates client-side, so that the scrollspy is populated with descriptions like 'Today,' 'Last Thursday,' or 'Next Tuesday.'

Topics
------
The topics JSON file contains hierarchical data. At the top level, this file is a list of objects. Each object represents a unit in the Physics class, such as Relativity or Simple Harmonic Motion. A unit object has three fields: 'unit-title' (its formal name), 'unit-description' (a brief high-level summary of the unit), and 'unit-classes'. The unit-classes key maps to a list of objects, each representing one day of physics class. Each class object has two mandatory fields: 'class-log' (a list of strings that describe what happened that day in Physics), and 'homework' (a string representing the homework to do that night). There is also the option to include another field, the 'additional' field, which can be used for anything.

Times
-----
The times JSON file is simply a list of dates, in a "MM/DD/YY" format (although any could be handled). When the server begins (or '/refreshjson' is sought), the time information is parsed into a programmatic format and zipped into the classes. The server will raise an Exception if there are not enough times to match to the existing classes (as represented by the topics JSON file); however, it is okay if there are more times than classes. We simply ignore the times that haven't been reached yet, so that units can be added sequentially. Specifically, times are parsed into unix time - (seconds since epoch) at which the given day begins, in PST - and a Python datetime object - an 'intelligent' (for lack of a better word) representation of the given date, again in PST.

Updating JSON Files
-------------------
Frequently, it will be necessary to change the JSON files from which the application draws its information. We explored two initial options to refresh the Python objects that contain our information:
1. Have the server initialize the objects once, when the server starts. If the JSON files are changed, restart the server.
2. Every time a request is made, reload the JSON files.
Option 1 is bad because the person to whom I'm handing off the project does not know want to ever interact with the server. Option 2 is bad because it would significantly slow down the server's response time (although I am in Python - so speed has never been a huge concern :D).
So, I settled on a compromise. The '/refreshjson' endpoint, which is linked to by no other links on the site, will refresh and reload all of the JSON files. This is an especially good solution, because it avoids having to turn the server off and on again, but also does not compromise normal page use times. 

Heroku
------
The project is currently hosted on Heroku's free cloud servers, but may in the future be moved to the Menlo School domain (*.menloschool.org), if the tech department cooperates.

