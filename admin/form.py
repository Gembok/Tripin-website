from google.appengine.ext import db

import utils
import view

class FormField:
    def __init__(self, model, property, name, instance_value, post_value):
        self.model = model
        self.property = property
        self.name = name
        self.instance_value = instance_value
        self.post_value = post_value
        self.model_value = None
        self.error_msg = None
    
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


class Select(FormField):
    pass


class Date(FormField):
    pass


class Link(FormField):
    filename = 'input'


class Email(FormField):
    filename = 'input'


class File(FormField):
    pass


class Reference(FormField):
    filename = 'select'
    
    def parse_value(self):
        return db.Key(self.post_value) if self.post_value else None
    
    def get_options(self):
        ref_model = getattr(self.model, self.name).reference_class
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
    
    def get_items(self):
        ref_model = getattr(self.model, self.name).item_type
        items = ref_model.all().fetch(10)
        items_dict = utils.to_dicts(items)
        print items_dict
        
    def render(self):
        return view.render_form(self.get_filename(), {
            'items': self.get_items(),
            'title': self.property.verbose_name
        })
