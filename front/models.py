from google.appengine.ext import db, blobstore

# Custom property classes
class BlobReferenceListProperty(db.ListProperty):
    def __init__(self, verbose_name):
        super(BlobReferenceListProperty, self).__init__(blobstore.BlobKey, verbose_name)

class ImageReferenceListProperty(BlobReferenceListProperty):
    pass

class ImageReferenceProperty(blobstore.BlobReferenceProperty):
    pass

# Model classes
class Biography(db.Model):
    text = db.TextProperty('Biographie')

class Album(db.Model):
    title = db.StringProperty('Titre')
    date = db.DateTimeProperty('Date')
    artwork = ImageReferenceProperty('Artwork')

class Player(db.Model):
    title = db.StringProperty('Titre')

class Song(db.Model):
    title = db.StringProperty('Titre')
    mp3 = blobstore.BlobReferenceProperty('Chanson')
    lyrics = db.TextProperty('Paroles')
    track = db.IntegerProperty('Track')
    album = db.ReferenceProperty(Album, 'Album')
    player = db.ReferenceProperty(Player, 'Player')

class Agenda(db.Model):
    title = db.StringProperty('Titre')
    date = db.DateTimeProperty('Date et heure')
    place = db.StringProperty('Lieu')
    link = db.LinkProperty('Lien')

class Photo(db.Model):
    title = db.StringProperty('Titre')
    credits = db.StringProperty('Credits')
    photos = ImageReferenceListProperty('Photos')
    concert = db.ReferenceProperty(Agenda, 'Concert')

class Video(db.Model):
    title = db.StringProperty('Titre')
    content = db.TextProperty('Contenu')

class Article(db.Model):
    title = db.StringProperty('Titre')
    text = db.TextProperty('Texte')

class Contact(db.Model):
    title = db.StringProperty('Titre')
    name = db.StringProperty('Nom')
    phone = db.StringProperty('Telephone')
    email = db.EmailProperty('Email')
    address = db.TextProperty('Adresse')

class Lien(db.Model):
    title = db.StringProperty('Titre')
    link = db.LinkProperty('Lien')

class Guestbook(db.Model):
    name = db.StringProperty('Nom')
    text = db.TextProperty('Message')

class Newsletter(db.Model):
    email = db.EmailProperty('Email')
