from google.appengine.ext import db, blobstore

import form
import front.models
import view

class AdminModel:
    model = None
    edit = []
    show = []
    
    def __init__(self, data=None, id=None, url=None):
        self.data = dict(data) if data else None
        self.url = url
        self.id = id
        self.blobstore = False
        self.instance = None
        self.get_instance()
        self.make_fields()
    
    def get_instance(self):
        """If not new form, gets the instance for values."""
        if self.id and not self.instance:
            self.instance = self.model.get_by_id(self.id)
    
    def make_fields(self):
        """Instantiates the form fields for the model's fields"""
        self.fields = []
        base_fields = self.model.properties()
        for name in self.edit:
            field = base_fields[name]
            instance_value = getattr(self.instance, name) if self.instance else None
            post_value = self.data[name] if self.data else None
            form_field = self.get_field_type(field)
            self.fields.append(form_field(field, name, instance_value, post_value))
    
    def get_field_type(self, field):
        """Returns the form field type."""
        if isinstance(field, db.StringProperty):
            form_field = form.Input
        elif isinstance(field, db.TextProperty):
            form_field = form.Textarea
        elif isinstance(field, blobstore.BlobReferenceProperty):
            self.blobstore = True
            form_field = form.File
        else:
            form_field = form.FormField
        return form_field
    
    def validate(self):
        """Validates all the fields according to field rules."""
        self.error_list = []
        if not self.instance:
            self.instance = self.model()
        for field in self.fields:
            if field.validate():
                setattr(self.instance, field.name, field.model_value)
            else:
                self.error_list.append(field.error())
        if len(self.error_list) > 0:
            return False
        return True
    
    def errors(self):
        return '<br>'.join(self.error_list)
    
    def save(self):
        return self.instance.put()
    
    def delete(self):
        return self.instance.delete()
    
    def action(self):
        """Returns blobstore upload url if model has blob."""
        return blobstore.create_upload_url(self.url) if self.blobstore else ''
    
    def render_form(self):
        """Renders the form with included fields rendered."""
        s = [f.render() for f in self.fields]
        data = {
            'form': ''.join(s),
            'id': self.id,
            'action': self.action()
        }
        return view.render_form('form.html', data)


class Member(AdminModel):
	model = front.models.Member
	show = ['name', 'bio']
	edit = show

registered = {'member': Member}