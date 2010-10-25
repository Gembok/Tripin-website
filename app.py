#!/usr/bin/env python
import cgi
import sys
sys.path.insert(0, 'ext')
import urllib
import logging

from google.appengine.ext import webapp
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import util, blobstore_handlers

import admin.handlers
import front.handlers


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
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication(routes, debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
