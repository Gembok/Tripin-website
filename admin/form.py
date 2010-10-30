import datetime

from google.appengine.ext import db, blobstore
from google.appengine.api import images

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
            (FileList,      front.models.BlobReferenceListProperty)
        ]
    
    def make_fields(self):
        """Instantiates the form fields for the model's fields"""
        for name, prop in self.edit:
            instance_value = self.model.get(name)
            post_value = self.data[name] if (self.data and self.data.has_key(name)) else instance_value
            form_field_class = self.get_field_type(prop)
            form_field = form_field_class(model=self.model, property=prop, name=name, instance_value=instance_value, post_value=post_value)
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
        self.refs.append(ReferenceList(self.model, modelname, refs))
    
    def upload(self, handler):
        for f in self.files:
            f.upload(handler)
            self.model.set(f.name, f.model_value)
        return True
    
    def validate(self):
        """Validates all the fields according to field rules."""
        for field in self.fields:
            if field.validate():
                self.model.set(field.name, field.model_value)
            else:
                self.errors.append(field.error())
        return len(self.errors) == 0
    
    def delete_blobs(self):
        for f in self.files:
            f.delete()
    
    def delete_blob(self, key):
        for f in self.files:
            f.delete(key)
            self.model.set(f.name, f.instance_value)
    
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
        if not self.files or not self.model.id: return ''
        s = [f.render() for f in self.files]
        return view.render_form('files.html', {
            'fields': ''.join(s),
            'id': self.model.id,
            'action': self.action()
        })


# Individual field
class FormField:
    def __init__(self, model=None, property=None, name='', instance_value=None, post_value=None, **kw):
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
    
    def file_value(self, handler=None):
        return self.instance_value
    
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
    def parse_value(self):
        if isinstance(self.property, db.IntegerProperty):
            return int(self.post_value)
        elif isinstance(self.property, db.FloatProperty):
            return float(self.post_value)
        else:
            return self.post_value


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
    def parse_value(self):
        if isinstance(self.post_value, datetime.datetime):
            return self.post_value
        else:
            format = '%Y-%m-%d %H:%M:%S'
            try:
                return datetime.datetime.strptime(self.post_value, format)
            except ValueError:
                format = '%Y-%m-%d'
            try:
                return datetime.datetime.strptime(self.post_value, format)
            except ValueError:
                return False


class Link(FormField):
    filename = 'input'


class Email(FormField):
    filename = 'input'


class Reference(FormField):
    filename = 'select'
    
    def parse_value(self):
        if isinstance(self.post_value, db.Model):
            return self.post_value.key()
        else:
            return db.Key(self.post_value) if self.post_value else None
    
    def get_options(self):
        ref_model = getattr(self.model.model, self.name).reference_class
        items = ref_model.all().fetch(10)
        items_dict = utils.to_dicts(items)
        for item in items_dict:
            self.check_if_selected(item)
        return items_dict
    
    def check_if_selected(self, item):
        if (self.instance_value) and (item['key'] == str(self.instance_value.key())):
            item['selected'] = 'selected="selected"'
    
    def render(self):
        return view.render_form(self.get_filename(), {
            'name': self.name,
            'title': self.property.verbose_name,
            'options': self.get_options()
        })


class ReferenceList(FormField):
    filename = 'list'
    
    def __init__(self, model, modelname, refs):
        self.model = model
        self.modelname = modelname
        self.refs = utils.to_dicts(refs)
    
    def render(self):
        return view.render_form(self.get_filename(), {
            'parent': self.model.name,
            'parent_id': self.model.id,
            'refs': self.refs,
            'model': self.modelname
        })


# Special properties for file fields
class FileField(FormField):
    pass

class File(FileField):
    def upload(self, handler):
        up = handler.get_uploads(self.name)
        if up:
            self.model_value = up[0].key()
            if self.instance_value:
                blobstore.delete(self.instance_value.key())
        else:
            self.model_value = self.instance_value
    
    def delete(self, key=None):
        if not self.instance_value: return
        if (not key) or (self.instance_value.key() == blobstore.BlobKey(key)):
            blobstore.delete(self.instance_value.key())
            self.instance_value = None
    
    def get_url(self):
        if self.instance_value:
            key = str(self.instance_value.key())
        else:
            return ''
        if isinstance(self.property, front.models.ImageReferenceListProperty):
            return images.get_serving_url(key)
        return '/serve/%s' % key
    
    def render(self):
        key = self.instance_value.key() if self.instance_value else ''
        return view.render_form(self.get_filename(), {
            'title': self.property.verbose_name,
            'id': self.model.id,
            'model': self.model.name,
            'name': self.name,
            'url': self.get_url(),
            'key': str(key)
        })


class FileList(FileField):
    def upload(self, handler):
        ups = handler.get_uploads(self.name)
        self.model_value = self.instance_value + [up.key() for up in ups]
            
    def delete(self, key=None):
        if not self.instance_value: return
        for i in range(0, len(self.instance_value)):
            if not key:
                blobstore.delete(str(self.instance_value[i]))
            elif str(self.instance_value[i]) == blobstore.BlobKey(key):
                blobstore.delete(key)
                del self.instance_value[i]
                return
        
    def get_urls(self):
        data = []
        for f in self.instance_value:
            if isinstance(self.property, front.models.ImageReferenceListProperty):
                url = images.get_serving_url(str(f))
            else:
                url = '/serve/%s' % str(f)
            data.append({
                'url': url,
                'key': str(f)
            })
        return data
    
    def render(self):
        return view.render_form(self.get_filename(), {
            'title': self.property.verbose_name,
            'name': self.name,
            'model': self.model.name,
            'id': self.model.id,
            'fields': range(1,10),
            'files': self.get_urls()
        })
