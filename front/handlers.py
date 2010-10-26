import logging
from datetime import datetime

from google.appengine.ext import webapp
from google.appengine.ext import db, blobstore

import view
import models
import utils

class AppHandler(webapp.RequestHandler):
    def render(self, filename, data):
        for k,v in data.iteritems():
            if isinstance(v, db.Model):
                data[k] = utils.to_dict(v)
            elif isinstance(v, list) and len(v) and isinstance(v[0], db.Model):
                data[k] = utils.to_dicts(v)
        view.render(self, filename, data)

class MainHandler(AppHandler):
    def get(self):
        self.render('main.html', {
            'test': 'ok',
            'contacts': self.contact(),
            'agenda': self.agenda(),
            'music': self.music()
        })
    
    def contact(self):
        return models.Contact().all().fetch(10)
    
    def agenda(self):
        agenda = models.Agenda().all().fetch(10)
        agenda = utils.to_dicts(agenda)
        for item in agenda:
            item['date'] = datetime.fromtimestamp(item['date']).strftime('%Y/%m/%d %H:%M')
        return agenda
    
    def music(self):
        return models.Player().all().get().song_set


routes = [
    (r'^/', MainHandler)
]