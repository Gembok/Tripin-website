from google.appengine.ext import db, blobstore

import form
import front.models

class AdminModel:
    model = None
    edit = []
    show = []
    
    def __init__(self, data=None, id=None, instance=None):
        self.data = dict(data) if data else None
        self.id = id
        self.fields = []
        self.new = self.model()
        self.instance = instance
        self.get_instance()
        self.make_fields()
    
    def get_instance(self):
        if self.id and not self.instance:
            self.instance = self.model.get(db.Key.from_path(self.model.kind(), id))
    
    def make_fields(self):
        base_fields = self.model.properties()
        for name in self.edit:
            field = base_fields[name]
            default = getattr(self.instance, name) if self.instance else field.default_value()
            data = self.data[name] if self.data else None
            if isinstance(field, db.StringProperty):
                form_field = form.Input
            elif isinstance(field, db.TextProperty):
                form_field = form.Textarea
            elif isinstance(field, blobstore.BlobReferenceProperty):
                form_field = form.File
            else:
                form_field = form.FormField
            self.fields.append(form_field(field, name, default, data))
    
    def validate(self):
        for field in self.fields:
            if field.validate():
                setattr(self.new, field.name, field.model_value)
            else:
                return False
        return True
    
    def save(self):
        return self.new.put()
    
    def render_form(self):
        s = ''
        for f in self.fields:
            s += f.render()
        return s


class Member(AdminModel):
	model = front.models.Member
	show = ['name', 'bio']
	edit = show

registered = {'member': Member}