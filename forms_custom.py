from google.appengine.ext import db, blobstore

class Form:
    def __init__(self, adminmodel):
        self.adminmodel = adminmodel
        self.model = adminmodel.model
        self.fields = []
        self.make_fields()
    
    def make_fields(self):
        base_fields = self.model.properties()
        for name in self.adminmodel.edit:
            field = base_fields[name]
            if isinstance(field, db.StringProperty):
                form_field = Input(name, field)
            elif isinstance(field, db.TextProperty):
                form_field = Textarea(name, field)
            elif isinstance(field, blobstore.BlobReferenceProperty):
                form_field = File(name, field)
            else:
                form_field = FormField(name, field)
            self.fields.append(form_field)

class FormField:
    def __init__(self, name, field):
        self.name = name
        self.field = field
    
    def render(self):
        return ""

class Input(FormField):
    def render(self):
        return '<input type="text" name="%s" value="%s" />' % (self.name, self.field.default_value())

class Textarea(FormField):
    def render(self):
        return '<textarea name="%s">%s</textarea>' % (self.name, self.field.default_value())

class File(FormField):
    def render(self):
        return '<input type="file" name="%s" />' % self.name