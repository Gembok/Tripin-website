import logging
from datetime import datetime

import simplejson as json
from google.appengine.ext import webapp
from google.appengine.ext import db, blobstore

import view
import models
import utils

class AppHandler(webapp.RequestHandler):
    def prepare(self, data):
        for k,v in data.iteritems():
            if isinstance(v, db.Model):
                data[k] = utils.to_dict(v)
            elif isinstance(v, list) and len(v) and isinstance(v[0], db.Model):
                data[k] = utils.to_dicts(v)
        return data
    
    def renderjson(self, filename, data):
        self.response.out.write(json.dumps({
            'data': self.prepare(data),
            'template': view.get_file(filename)
        }))
    
    def render(self, filename, data):
        data = self.prepare(data)
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

class BioHandler(AppHandler):
    def get(self):
        bio = models.Biography().all().get()
        self.renderjson('bio.html', {
            'bio': bio.text
        })

class MusicHandler(AppHandler):
    def get(self, id):
        albums = models.Album().all().fetch(10)
        albums = utils.to_dicts(albums, 200)
        for item in albums:
            item['date'] = datetime.fromtimestamp(item['date']).strftime('%Y')
        self.renderjson('music.html', {
            'albums': albums
        })

routes = [
    (r'^/bio/?', BioHandler),
    (r'^/music/?(\d+)?/?', MusicHandler),
    (r'^/', MainHandler)
]