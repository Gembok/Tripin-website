import logging
from datetime import datetime

import simplejson as json
import markdown2
from google.appengine.ext import webapp
from google.appengine.ext import db, blobstore
from google.appengine.api import images

import view
import models
import utils

class AppHandler(webapp.RequestHandler):
    def prepare(self, data=None):
        if not data: return None
        for k,v in data.iteritems():
            if isinstance(v, db.Model):
                data[k] = utils.to_dict(v)
            elif isinstance(v, list) and len(v) and isinstance(v[0], db.Model):
                data[k] = utils.to_dicts(v)
        return data
    
    def renderjson(self, filename, data=None):
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
            'bio': markdown2.markdown(bio.text)
        })


class MusicHandler(AppHandler):
    def get(self, id):
        id = int(id or 0)
        self.m = models.Album()
        self.renderjson('music.html', {
            'albums': self.albums(),
            'album': self.album(id)
        })
    
    def albums(self):
        albums = self.m.all().fetch(10)
        albums = utils.to_dicts(albums)
        for item in albums:
            item['date'] = datetime.fromtimestamp(item['date']).strftime('%Y')
            item['artwork'] = images.get_serving_url(item['artwork'], 90)
        return albums
    
    def album(self, id):
        if not id:
            album = self.m.all().get()
        else:
            album = self.m.get_by_id(id)
        albumd = utils.to_dict(album)
        albumd['artwork'] = images.get_serving_url(albumd['artwork'], 320)
        albumd['songs'] = self.songs(album)
        return albumd
    
    def songs(self, album):
        songs = album.song_set
        return utils.to_dicts(songs)


class TextHandler(AppHandler):
    def get(self, id):
        pass


class MediaHandler(AppHandler):
    def get(self):
        self.renderjson('media.html')


class PhotosHandler(AppHandler):
    def get(self, id):
        id = int(id or 0)
        pass


class VideosHandler(AppHandler):
    def get(self, id):
        id = int(id or 0)
        pass


class PresseHandler(AppHandler):
    def get(self, id):
        id = int(id or 0)
        pass


routes = [
    (r'^/bio/?', BioHandler),
    (r'^/music/?(\d+)?/?', MusicHandler),
    (r'^/texts/?(\d+)?/?', TextHandler),
    (r'^/photos/?(\d+)?/?', PhotosHandler),
    (r'^/videos/?(\d+)?/?', VideosHandler),
    (r'^/presse/?(\d+)?/?', PresseHandler),
    (r'^/media/?', MediaHandler),
    (r'^/', MainHandler)
]
