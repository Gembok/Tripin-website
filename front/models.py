from google.appengine.ext import db, blobstore

class Member(db.Model):
    name = db.StringProperty('Nom', required=True, default='name')
    bio = db.TextProperty('Biographie', required=True, default='biography')
    image = blobstore.BlobReferenceProperty('Image')