import view

class FormField:
    def __init__(self, property, name, instance_value, post_value):
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
        if self.instance_value is not None:
            return self.instance_value
        elif self.post_value is not None:
            return self.post_value
        else:
            return self.property.default_value()
    
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
        return bool(self.post_value)
    
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

