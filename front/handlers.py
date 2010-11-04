import logging
from datetime import datetime
import urllib

import simplejson as json
import markdown2
from google.appengine.ext import webapp
from google.appengine.ext import db, blobstore
from google.appengine.api import images

import view
import models
import utils

serve_url = '/serve/%s'

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
            'player': self.player(),
            'links': self.links()
        })
    
    def contact(self):
        return models.Contact.all().fetch(10)
    
    def agenda(self):
        agenda = models.Agenda.all().filter('date >=', datetime.now()).fetch(100)
        agendad = utils.to_dicts(agenda)
        for item in agendad:
            item['date'] = datetime.fromtimestamp(item['date']).strftime('%Y/%m/%d %H:%M')
        return agendad
    
    def player(self):
        try:
            songs = models.Player.all().get().song_set
        except AttributeError:
            return ''
        url = '/serve/%s'
        data = {
            'mp3': '|'.join([url % str(s.mp3.key()) for s in songs]),
            'title': '|'.join([s.title for s in songs])
        }
        return urllib.urlencode(data).replace('%3D','=')
    
    def links(self):
        links = models.Lien.all().fetch(10)
        return utils.to_dicts(links)


class BioHandler(AppHandler):
    def get(self):
        bio = models.Biography.all().get()
        self.renderjson('bio.html', utils.to_dict(bio))


class MusicHandler(AppHandler):
    def get(self, id):
        id = int(id or 0)
        self.m = models.Album
        self.renderjson('music.html', {
            'albums': self.albums(),
            'album': self.album(id)
        })
    
    def albums(self):
        albums = self.m.all().fetch(10)
        albums = utils.to_dicts(albums)
        for item in albums:
            item['date'] = datetime.fromtimestamp(item['date']).strftime('%Y')
            item['artwork'] = images.get_serving_url(item['artwork'], 104, crop=True)
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
        id = int(id or 0)
        try:
            self.q = models.Album.gql('WHERE title = :1', 'Tomber les Masques').get().song_set
            self.q.order('track')
            data = {
                'texts': utils.to_dicts(self.q),
                'text': self.text(id)
            }
        except AttributeError:
            data = {'songs': [], 'song': {}}
        self.renderjson('texts.html', data)
    
    def text(self, id):
        if not id:
            song = self.q.get()
        else:
            song = models.Song.get_by_id(id)
        songd = utils.to_dict(song)
        songd['album'] = song.album.title
        songd['mp3'] = serve_url % songd['mp3']
        return songd


class MediaHandler(AppHandler):
    def get(self):
        self.renderjson('media.html')


class PhotosHandler(AppHandler):
    def get(self, id):
        id = int(id or 0)
        self.m = models.Photo
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
        self.m = models.Video
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
        self.m = models.Article
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
        key = itemd['img']
        itemd['img'] = images.get_serving_url(key, 200)
        itemd['img_big'] = images.get_serving_url(key, 1024)
        return itemd


class NewsletterHandler(AppHandler):
    def get(self, delete):
        email = self.request.get('email', None)
        if delete:
            self.delete(email)
        else:
            self.subscribe(email)
    
    def subscribe(self, email):
        if not email:
            self.response.out.write('0')
            return
        if models.Newsletter.gql('WHERE email = :1', email).count():
            self.response.out.write('2')
            return
        models.Newsletter(email=email).put()
        self.response.out.write('1')
    
    def delete(self, email):
        if not email:
            self.reponse.out.write('Email non valide')
            return
        query = models.Newsletter.gql('WHERE email = :1', email)
        if query.count():
            query.get().delete()
            self.response.out.write('L\'addresse email "%s" a removed de la newsletter.' % email)
        else:
            self.response.out.write('...')


class GuestbookHandler(AppHandler):
    def get(self):
        mess = models.Guestbook.all().fetch(100)
        messd = utils.to_dicts(mess)
        messd = sorted(messd, lambda x,y: cmp(x['id'], y['id']), reverse=True)
        self.renderjson('guestbook.html', {
            'mess': messd
        })
    
    def post(self):
        name = self.request.get('name', '')
        text = self.request.get('text', '')
        if name and text:
            models.Guestbook(name=name, text=text).put()
            self.response.out.write('1')
        else:
            self.response.out.write('0')


routes = [
    (r'^/bio/?', BioHandler),
    (r'^/music/?(\d+)?/?', MusicHandler),
    (r'^/texts/?(\d+)?/?', TextHandler),
    (r'^/photos/?(\d+)?/?', PhotosHandler),
    (r'^/videos/?(\d+)?/?', VideosHandler),
    (r'^/presse/?(\d+)?/?', PresseHandler),
    (r'^/media/?', MediaHandler),
    (r'^/newsletter/?(\w+)?/?', NewsletterHandler),
    (r'^/guestbook/?', GuestbookHandler),
    (r'^/', MainHandler)
]
