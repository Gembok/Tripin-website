from google.appengine.ext import db, blobstore

import form
import front.models
import view

class AdminModel:
    model = None
    edit = []
    show = []
    mappings = [
        (form.Input,            (db.StringProperty, db.IntegerProperty, db.FloatProperty)),
        (form.Textarea,         db.TextProperty),
        (form.Checkbox,         db.BooleanProperty),
        (form.Date,             (db.DateProperty, db.DateTimeProperty, db.TimeProperty)),
        (form.Email,            db.EmailProperty),
        (form.Link,             db.LinkProperty),
        (form.Reference,        db.ReferenceProperty)
    ]
    
    def __init__(self, data=None, id=None, upload_url=None):
        self.data = dict(data) if data else None
        self.upload_url = upload_url
        self.id = id
        self.blobstore = {}
        self.instance = None
        self.get_instance()
    
    def build_form(self):
        self.get_editfields()
        self.make_fields()
        self.make_file_fields()
    
    def get_instance(self):
        """If not new form, gets the instance for values."""
        if self.id and not self.instance:
            self.instance = self.model.get_by_id(self.id)
    
    def get_editfields(self):
        self.allfields = {}
        base_fields = self.model.properties()
        for name in self.edit:
            try:
                self.allfields[name] = base_fields[name]
            except KeyError: pass
    
    def make_fields(self):
        """Instantiates the form fields for the model's fields"""
        self.form_fields = []
        for name, field in self.allfields.iteritems():
            self.check_blobstore(name, field)
            instance_value = getattr(self.instance, name) if self.instance else None
            post_value = self.data[name] if (self.data and self.data.has_key(name)) else None
            form_field = self.get_field_type(field)
            if form_field:
                self.form_fields.append(form_field(self.model, field, name, instance_value, post_value))
        self.check_references()
    
    def get_field_type(self, field):
        """Returns the form field type."""
        for mapping in self.mappings:
            if isinstance(field, mapping[1]):
                return mapping[0]
        return None
    
    def check_blobstore(self, name, field):
        if isinstance(field, blobstore.BlobReferenceProperty):
            self.blobstore[name] = field
    
    def make_file_fields(self):
        self.file_fields = []
        for name, field in self.blobstore.iteritems():
            blob = getattr(self.instance, name, None)
            self.file_fields.append(form.File(self.model, property=field, name=name, key=blob.key()))
    
    def check_references(self):
        """Add reference list field if the model has references"""
        for key, model in registered.iteritems():
            collection = '%s_set' % model.__name__.lower()
            try:
                refs = getattr(self.instance, collection)
                self.form_fields.append(form.ReferenceList(key, refs))
            except AttributeError: pass
    
    def validate(self):
        """Validates all the fields according to field rules."""
        self.error_list = []
        if not self.instance:
            self.instance = self.model()
        for field in self.form_fields:
            if field.validate():
                setattr(self.instance, field.name, field.model_value)
            else:
                self.error_list.append(field.error())
        return len(self.error_list) == 0
    
    def errors(self):
        try:
            return '<br>'.join(self.error_list)
        except AttributeError: 
            return ''
    
    def save(self):
        return self.instance.put()
    
    def delete(self):
        return self.instance.delete()
    
    def action(self):
        """Returns blobstore upload url if model has blob."""
        return blobstore.create_upload_url(self.upload_url) if self.blobstore else ''
    
    def render_form(self):
        """Renders the form with included fields rendered."""
        s = [f.render() for f in self.form_fields]
        return view.render_form('form.html', {
            'fields': ''.join(s),
            'errors': self.errors(),
            'id': self.id
        })
    
    def render_file_form(self):
        if not self.file_fields: return ''
        s = [f.render() for f in self.file_fields]
        return view.render_form('files.html', {
            'fields': ''.join(s),
            'id': self.id,
            'action': self.action()
        })

# User classes
class Member(AdminModel):
	model = front.models.Member
	show = ['name', 'bio', 'image', 'one', 'email', 'link']
	edit = show


class Concert(AdminModel):
    model = front.models.Concert
    show = ['title', 'member']
    edit = show

registered = {'member': Member, 'concert': Concert}