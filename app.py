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
    def to_dict(self, model):
        data = {}
        for key, value in model.properties().iteritems():
            val = value.get_value_for_datastore(model)
            if isinstance(val, datetime.datetime):
                ms = time.mktime(val.utctimetuple()) * 1000
                ms += getattr(value, 'microseconds', 0) / 1000
                val = int(ms)
            elif isinstance(val, db.Model):
                val = self.to_dict(val)
            data[key] = val
        return data
    
    def render(self, filename, data):
		view.render(self, filename, data)


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        if not blobstore.get(resource):
            self.error(404)
        else:
            self.send_blob(resource)

routes = [
    # (r'^/test', front.handlers.TestHandler),
    (r'^/admin/?$', admin.handlers.ModelsHandler),
    (r'^/admin/list/(\w+)/?$', admin.handlers.ListHandler),
    (r'^/admin/edit/(\w+)/?$', admin.handlers.EditHandler),
    (r'^/admin/delete/(\w+)/?$', admin.handlers.DeleteHandler),
    (r'^/admin/upload/(\w+)/?$', admin.handlers.UploadHandler),
    (r'^/admin/deleteblob/(\w+)/?$', admin.handlers.DeleteBlobHandler),
    (r'^/serve/([^/]+)?', ServeHandler)
    # (r'^/(.*)/?$', front.handlers.MainHandler),
]

def main():
	application = webapp.WSGIApplication(routes, debug=True)
	util.run_wsgi_app(application)

if __name__ == '__main__':
	main()
