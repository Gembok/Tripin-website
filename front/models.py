from google.appengine.ext import db, blobstore

# Custom property classes
class BlobReferenceListProperty(db.ListProperty):
    def __init__(self, verbose_name):
        super(BlobReferenceListProperty, self).__init__(blobstore.BlobKey, verbose_name)

# Model classes
class Member(db.Model):
    name = db.StringProperty('Nom', required=False)
    bio = db.TextProperty('Biographie', required=False)
    image = blobstore.BlobReferenceProperty('Image')
    one = db.BooleanProperty('Bool')
    email = db.EmailProperty('Email')
    link = db.LinkProperty('Lien')
    datea = db.DateTimeProperty('Date')
    files = BlobReferenceListProperty('Files')


class Concert(db.Model):
    title = db.StringProperty('Title')
    member = db.ReferenceProperty(Member, 'Member')
