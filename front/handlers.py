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
        songs = models.Player().all().get().song_set
        songsd = []
        for s in songs:
            songsd.append({
                'url': '/serve/%s' % s.key()
            })


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
        self.m = models.Photo()
        self.renderjson('photos.html', {
          'photos': self.photos(),
          'photo': self.photo(id)
        })
        
    def photos(self):
        photos = self.m.all().fetch(10)
        photosd = utils.to_dicts(photos)
        for item in photosd:
            item['photos'] = []
            item['img'] = images.get_serving_url(item['img'], 80, True)
        return photosd
    
    def photo(self, id):
        if not id:
            photo = self.m.all().get()
        else:
            photo = self.m.get_by_id(id)
        photod = utils.to_dict(photo)
        photod['concert'] = photo.concert.title
        for i in range(len(photod['photos'])):
            key = str(photod['photos'][i])
            url = images.get_serving_url(key, 80, True)
            url_big = images.get_serving_url(key, 720)
            photod['photos'][i] = {'url': url, 'url_big': url_big}
        return photod


class VideosHandler(AppHandler):
    def get(self, id):
        id = int(id or 0)
        self.m = models.Video()
        self.renderjson('videos.html', {
            'videos': self.videos(),
            'video': self.video(id)
        })
    
    def videos(self):
        videos = self.m.all().fetch(10)
        videosd = utils.to_dicts(videos)
        for item in videosd:
            item['content'] = ''
        return videosd
    
    def video(self, id):
        if not id:
            video = self.m.all().get()
        else:
            video = self.m.get_by_id(id)
        return utils.to_dict(video)


class PresseHandler(AppHandler):
    def get(self, id):
        id = int(id or 0)
        self.m = models.Article()
        self.renderjson('presse.html', {
            'articles': self.articles(),
            'article': self.article(id)
        })
    
    def articles(self):
        items = self.m.all().fetch(10)
        itemsd = utils.to_dicts(items)
        for item in itemsd:
            item['text'] = ''
            item['img'] = ''
        return itemsd

    def article(self, id):
        if not id:
            item = self.m.all().get()
        else:
            item = self.m.get_by_id(id)
        itemd = utils.to_dict(item)
        itemd['text'] = markdown2.markdown(itemd['text'])
        key = itemd['img']
        itemd['img'] = images.get_serving_url(key, 200)
        itemd['img_big'] = images.get_serving_url(key, 1024)
        return itemd


class NewsletterHandler(AppHandler):
    def get(self):
        email = self.request.get('email', None)
        if not email:
            self.response.out.write('{confirm: 0}')
            return
        if models.Newsletter.gql('WHERE email = :1', email).count():
            self.response.out.write('{confirm: 2}')
            return
        models.Newsletter(email=email).put()
        self.response.out.write('{confirm: 1}')


routes = [
    (r'^/bio/?', BioHandler),
    (r'^/music/?(\d+)?/?', MusicHandler),
    (r'^/texts/?(\d+)?/?', TextHandler),
    (r'^/photos/?(\d+)?/?', PhotosHandler),
    (r'^/videos/?(\d+)?/?', VideosHandler),
    (r'^/presse/?(\d+)?/?', PresseHandler),
    (r'^/media/?', MediaHandler),
    (r'^/newsletter/?', NewsletterHandler),
    (r'^/', MainHandler)
]
