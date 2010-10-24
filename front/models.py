from google.appengine.ext import db, blobstore

# Custom property classes
class FileListProperty(db.ListProperty):
    pass

class BlobListProperty(db.ListProperty):
    def __init__(self, m_size):
        self.m_size = m_size
        super(BlobListProperty, self).__init__(db.Blob)


# Model classes
class Member(db.Model):
    name = db.StringProperty('Nom', required=False)
    bio = db.TextProperty('Biographie', required=False)
    # image = blobstore.BlobReferenceProperty('Image')
    # one = db.BooleanProperty('Bool', default=True)
    # email = db.EmailProperty('Email', required=False)
    # link = db.LinkProperty('Lien')
    # files_blob = BlobListProperty((100, 100))
    files = FileListProperty(blobstore.BlobKey, 'Files')


class Concert(db.Model):
    title = db.StringProperty('Title')
    member = db.ReferenceProperty(Member, 'Member')