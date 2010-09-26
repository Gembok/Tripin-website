from google.appengine.ext import db, blobstore

import view

class Form:
    model = None
    edit = []
    show = []
    
    def __init__(self, data=None, instance=None):
        self.data = data
        self.instance = instance
        self.fields = []
        self.new = self.model()
        self.make_fields()
    
    def make_fields(self):
        base_fields = self.model.properties()
        for name in self.edit:
            field = base_fields[name]
            default = getattr(self.instance, name) if self.instance else field.default_value()
            data = self.data[name] if self.data else None
            if isinstance(field, db.StringProperty):
                form_field = Input
            elif isinstance(field, db.TextProperty):
                form_field = Textarea
            elif isinstance(field, blobstore.BlobReferenceProperty):
                form_field = File
            else:
                form_field = FormField
            self.fields.append(form_field(field, name, default, data))
    
    def validate(self):
        for field in self.fields:
            if field.validate():
                setattr(self.new, field.name, field.model_value)
            else:
                return False
    
    def save(self):
        return self.new.put()
    
    def render(self):
        s = ''
        for f in self.fields:
            s += f.render()
        return s
    

class FormField:
    def __init__(self, property, name, default_value, post_value):
        self.property = property
        self.name = name
        self.default_value = default_value
        self.post_value = post_value
        self.model_value = None
    
    def validate(self):
        try:
            self.model_value = self.property.validate(self.raw_value)
        except:
            return False
    
    def render(self):
        f = self.__class__.__name__.lower()+'.html'
        data = {
            'title': self.property.verbose_name,
            'name': self.name,
            'default': self.default_value
        }
        return view.render_form(f, data)

class Input(FormField):
    pass

class Textarea(FormField):
    pass

class File(FormField):
    pass