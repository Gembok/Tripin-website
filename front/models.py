from google.appengine.ext import db, blobstore

class Concert(db.Model):
    title = db.StringProperty('Title')

class Member(db.Model):
    name = db.StringProperty('Nom', required=True)
    bio = db.TextProperty('Biographie', required=False)
    # image = blobstore.BlobReferenceProperty('Image')
    # one = db.BooleanProperty('Bool', default=True)
    # email = db.EmailProperty('Email', required=True)
    # link = db.LinkProperty('Lien')
    # concert = db.ReferenceProperty(Concert, 'Concert')
    refs = db.ListProperty(Concert, 'Refs')