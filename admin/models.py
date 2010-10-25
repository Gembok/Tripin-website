import front.models
import adminmodel
import form

class AdminModel:
    model = None
    edit = []
    show = []
    
    def __init__(self, id=None, name=''):
        self.id = id
        self.name = name
        self.instance = None
        self.get_instance()
    
    def make_form(self, post_data={}, upload_url=None):
        self.form = form.Form(self, self.get_edit_fields(), dict(post_data), upload_url)
        self.form.make_fields()
        self.check_references()
    
    def get_instance(self):
        """Get old instance or new empty one."""
        if self.id and not self.instance:
            self.instance = self.model.get_by_id(self.id)
        else:
            self.instance = self.model()
    
    def get_edit_fields(self):
        edit_fields = []
        base_fields = self.model.properties()
        for name in self.edit:
            try:
                edit_fields.append((name, base_fields[name]))
            except KeyError: pass
        return edit_fields
    
    def check_references(self):
        """Add reference list field if the model has references"""
        for key, model in registered.iteritems():
            collection = '%s_set' % model.__name__.lower()
            try:
                refs = getattr(self.instance, collection)
                self.form.add_ref(key, refs)
            except Exception: pass
    
    def get(self, name):
        try:
            return getattr(self.instance, name, None)
        except:
            return None
    
    def get_blob_property(self, name):
        prop_name = '%s_blob' % name
        prop = getattr(self.model, prop_name, None)
        return (prop, prop_name)
    
    def set(self, name, value):
        setattr(self.instance, name, value)
    
    def upload(self, handler):
        self.form.upload(handler)
        self.save()
    
    def save(self):
        if self.form.validate():
            return self.instance.put()
        else:
            return False
    
    def delete(self):
        self.form.delete_blobs()
        return self.instance.delete()
    
    def delete_blob(self, key):
        self.form.delete_blob(key)
        self.save()
    
    def render(self):
        return {
            'form': self.form.render_form(),
            'files':self.form.render_files()
        }


# User classes
class Biography(AdminModel):
    model = front.models.Biography
    edit = ['text']
    show = ['text']

class Album(AdminModel):
    model = front.models.Album
    edit = ['title', 'date']
    show = ['title']

class Song(AdminModel):
    model = front.models.Song
    edit = ['title', 'track', 'mp3', 'lyrics', 'album']
    show = ['title', 'track']

class Photo(AdminModel):
    model = front.models.Photo
    edit = ['title', 'concert', 'credits', 'photos']
    show = ['title']

class Video(AdminModel):
    model = front.models.Video
    edit = ['title', 'content']
    show = ['title']

class Article(AdminModel):
    model = front.models.Article
    edit = ['titre', 'text']
    show = ['text']

class Agenda(AdminModel):
    model = front.models.Agenda
    edit = ['title', 'date', 'place']
    show = edit

class Contact(AdminModel):
    model = front.models.Contact
    edit = ['title', 'name', 'tel', 'email', 'address']
    show = ['name']

class Lien(AdminModel):
    model = front.models.Lien
    edit = ['title', 'link']
    show = edit

class Guestbook(AdminModel):
    model = front.models.Guestbook
    edit = ['name', 'text']
    show = ['name']

class Newsletter(AdminModel):
    model = front.models.Newsletter
    edit = ['email']
    show = ['email']

registered = {
    'biographie': Biography,
    'albums': Album,
    'songs': Song,
    'photos': Photo,
    'videos': Video,
    'articles': Article,
    'agenda': Agenda,
    'contacts': Contact,
    'liens': Lien,
    'guestbook': Guestbook,
    'newsletter': Newsletter
}