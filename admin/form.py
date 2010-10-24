from google.appengine.ext import db, blobstore

import front.models
import utils
import view

# Main form
class Form:
    def __init__(self, model, edit, data, upload_url):
        self.fields = []
        self.files = []
        self.refs = []
        self.errors = []
        self.model = model
        self.edit = edit
        self.data = data
        self.upload_url = upload_url
        self.mappings = [
            (Input,         (db.StringProperty, db.IntegerProperty, db.FloatProperty)),
            (Textarea,      db.TextProperty),
            (Checkbox,      db.BooleanProperty),
            (Date,          (db.DateProperty, db.DateTimeProperty, db.TimeProperty)),
            (Email,         db.EmailProperty),
            (Link,          db.LinkProperty),
            (Reference,     db.ReferenceProperty),
            (File,          blobstore.BlobReferenceProperty),
            (FileList,      front.models.FileListProperty)
        ]
    
    def make_fields(self):
        """Instantiates the form fields for the model's fields"""
        for name, prop in self.edit:
            instance_value = getattr(self.model.instance, name, None)
            post_value = self.data[name] if (self.data and self.data.has_key(name)) else None
            form_field_class = self.get_field_type(prop)
            form_field = form_field_class(self.model, prop, name, instance_value, post_value)
            self.add(form_field)
    
    def add(self, form_field):
        if isinstance(form_field, FileField):
            self.files.append(form_field)
        else:
            self.fields.append(form_field)
    
    def get_field_type(self, field):
        """Returns the form field type."""
        for mapping in self.mappings:
            if isinstance(field, mapping[1]):
                return mapping[0]
        return None
    
    def add_ref(self, modelname, refs):
        self.refs.append(ReferenceList(modelname, refs))
    
    def validate(self):
        """Validates all the fields according to field rules."""
        for field in self.fields:
            if field.validate():
                self.model.set(field.name, field.model_value)
            else:
                self.errors.append(field.error())
        return len(self.errors) == 0
    
    def get_errors(self):
        return '<br>'.join(self.errors)
    
    def action(self):
        """Returns blobstore upload url if model has blob."""
        return blobstore.create_upload_url(self.upload_url)
    
    def render_form(self):
        """Renders the form with included fields rendered."""
        s = [f.render() for f in self.fields]
        r = [f.render() for f in self.refs]
        return view.render_form('form.html', {
            'fields': ''.join(s),
            'refs': ''.join(r),
            'errors': self.get_errors(),
            'id': self.model.id
        })
    
    def render_files(self):
        if not self.files: return ''
        s = [f.render() for f in self.files]
        return view.render_form('files.html', {
            'fields': ''.join(s),
            'id': self.model.id,
            'action': self.action()
        })


# Individual field
class FormField:
    def __init__(self, model, property=None, name='', instance_value=None, post_value=None, **kw):
        self.model = model
        self.property = property
        self.name = name
        self.instance_value = instance_value
        self.post_value = post_value
        self.model_value = None
        self.error_msg = None
        for key, val in kw.iteritems():
            setattr(self, key, val)
    
    def validate(self):
        newval = self.parse_value()
        try:
            self.model_value = self.property.validate(newval)
            return True
        except Exception, e:
            self.error_msg = '%s has error: %s' % (self.name, e)
            return False
    
    def parse_value(self):
        return self.post_value
    
    def error(self):
        return self.error_msg
    
    def value_for_form(self):
        if self.post_value is not None:
            return self.post_value
        elif self.instance_value is not None:
            return self.instance_value
        else:
            return self.property.default_value() or ''
    
    def get_filename(self):
        try:
            return '%s.html' % self.filename
        except AttributeError:
            return self.__class__.__name__.lower()+'.html'
    
    def render(self):
        return view.render_form(self.get_filename(), {
            'title': self.property.verbose_name,
            'name': self.name,
            'default': self.value_for_form()
        })


# Custom form fields
class Input(FormField):
    pass


class Textarea(FormField):
    pass


class Checkbox(FormField):
    def parse_value(self):
        return bool(self.post_value) if self.post_value else False
    
    def render(self):
        return view.render_form(self.get_filename(), {
            'title': self.property.verbose_name,
            'name': self.name,
            'checked': 'checked="checked"' if self.value_for_form() else ""
        })


class Date(FormField):
    pass


class Link(FormField):
    filename = 'input'


class Email(FormField):
    filename = 'input'


class Reference(FormField):
    filename = 'select'
    
    def parse_value(self):
        return db.Key(self.post_value) if self.post_value else None
    
    def get_options(self):
        ref_model = getattr(self.model.model, self.name).reference_class
        items = ref_model.all().fetch(10)
        items_dict = utils.to_dicts(items)
        for item in items_dict:
            self.check_if_selected(item)
        return items_dict
    
    def check_if_selected(self, item):
        if (self.instance_value) and (item['key'] == self.instance_value.key()):
            item['selected'] = 'selected="selected"'
    
    def render(self):
        return view.render_form(self.get_filename(), {
            'name': self.name,
            'title': self.property.verbose_name,
            'options': self.get_options()
        })


class ReferenceList(FormField):
    filename = 'list'
    
    def __init__(self, modelname, refs):
        self.modelname = modelname
        self.refs = utils.to_dicts(refs)
    
    def render(self):
        return view.render_form(self.get_filename(), {
            'refs': self.refs,
            'model': self.modelname
        })


class FileField(FormField):
    pass

class File(FileField):
    def render(self):
        return view.render_form(self.get_filename(), {
            'title': self.property.verbose_name,
            'name': self.name,
            'key': str(self.instance_value.key() if self.instance_value else '')
        })


class FileList(FileField):
    def get_files(self):
        files = getattr(self.model.get_by_id(), self.name)
        return [str(f) for f in files]
    
    def render(self):
        return view.render_form(self.get_filename(), {
            'title': self.property.verbose_name,
            'name': self.name,
            'fields': range(1,10),
            'keys': self.get_files()
        })
