from google.appengine.ext import db, blobstore

class Member(db.Model):
	name = db.StringProperty('Nom', required=True)
	bio = db.TextProperty('Biographie', required=True)
	image = blobstore.BlobReferenceProperty('Image')