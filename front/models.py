from google.appengine.ext import db, blobstore

class Member(db.Model):
	name = db.StringProperty('Nom', required=True, default='a')
	bio = db.TextProperty('Biographie', required=True, default='a')
	image = blobstore.BlobReferenceProperty('Image')