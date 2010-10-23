from google.appengine.ext import db, blobstore

class Member(db.Model):
    name = db.StringProperty('Nom', required=False)
    bio = db.TextProperty('Biographie', required=False)
    # image = blobstore.BlobReferenceProperty('Image')
    # one = db.BooleanProperty('Bool', default=True)
    # email = db.EmailProperty('Email', required=False)
    # link = db.LinkProperty('Lien')
    files = db.ListProperty(blobstore.BlobKey, 'Files')


class Concert(db.Model):
    title = db.StringProperty('Title')
    member = db.ReferenceProperty(Member, 'Member')