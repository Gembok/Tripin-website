from google.appengine.ext import webapp

import view
import models

class AppHandler(webapp.RequestHandler):
	pass

class MainHandler(AppHandler):
	def get(self):
		self.response.out.write('adf')
