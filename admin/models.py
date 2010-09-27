from google.appengine.ext import db, blobstore

import form
import front.models
import view

class AdminModel:
    model = None
    edit = []
    show = []
    
    def __init__(self, data=None, id=None, instance=None, url=None):
        self.data = dict(data) if data else None
        self.url = url
        self.id = id
        self.fields = []
        self.blobstore = False
        self.error_list = []
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
            instance_value = getattr(self.instance, name) if self.instance else None
            post_value = self.data[name] if self.data else None
            if isinstance(field, db.StringProperty):
                form_field = form.Input
            elif isinstance(field, db.TextProperty):
                form_field = form.Textarea
            elif isinstance(field, blobstore.BlobReferenceProperty):
                self.blobstore = True
                form_field = form.File
            else:
                form_field = form.FormField
            self.fields.append(form_field(field, name, instance_value, post_value))
    
    def validate(self):
        for field in self.fields:
            if field.validate():
                setattr(self.new, field.name, field.model_value)
            else:
                self.error_list.append(field.error())
                return False
        return True
    
    def errors(self):
        return '<br>'.join(self.error_list)
    
    def save(self):
        return self.new.put()
    
    def action(self):
        return blobstore.create_upload_url(self.url) if self.blobstore else ''
    
    def render_form(self):
        s = [f.render() for f in self.fields]
        data = {
            'form': ''.join(s),
            '_id': self.id,
            'action': self.action()
        }
        return view.render_form(data)


class Member(AdminModel):
	model = front.models.Member
	show = ['name', 'bio']
	edit = show

registered = {'member': Member}