from jinja2 import Markup
from datetime import datetime

class momentjs(object):
	def __init__(self, timestamp):
		self.timestamp = int(timestamp) #Time since epoch

	def render(self, fmt):
		return Markup('<script>\ndocument.write(moment.unix("{0}").{1})\n</script>'.format(self.timestamp, fmt))
		# return Markup('<script>\ndocument.write(moment({0}).{1});\n</script>'.format(self.timestamp, fmt))

	def format(self, fmt):
		return self.render('format("{0}")'.format(fmt))

	def calendar(self):
		return self.render("calendar()")

	def fromNow(self):
		return self.render("fromNow()")