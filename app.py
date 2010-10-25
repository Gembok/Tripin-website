#!/usr/bin/env python
import cgi
import config
import sys
sys.path.insert(0, config.EXT)
import urllib

from google.appengine.ext import webapp
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import util, blobstore_handlers

import admin.handlers
import front.handlers

class BaseHandler(webapp.RequestHandler):
    def render(self, filename, data):
		view.render(self, filename, data)


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        if not blobstore.get(resource):
            self.error(404)
        else:
            self.send_blob(resource)

routes = front.handlers.routes + admin.handlers.routes + [
    (r'^/serve/([^/]+)?', ServeHandler)
]

def main():
	application = webapp.WSGIApplication(routes, debug=True)
	util.run_wsgi_app(application)

if __name__ == '__main__':
	main()
