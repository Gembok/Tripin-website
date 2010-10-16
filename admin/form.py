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
        try:
            self.model_value = self.property.validate(self.post_value)
            return True
        except Exception, e:
            self.error_msg = '%s has error: %s' % (self.name, e)
            return False
    
    def error(self):
        return self.error_msg
    
    def value(self):
        if self.instance_value is not None:
            return self.instance_value
        elif self.post_value is not None:
            return self.post_value
        else:
            return self.property.default_value()
    
    def get_filename(self):
        return self.__class__.__name__.lower()+'.html'
    
    def render(self):
        f = self.get_filename()
        data = {
            'title': self.property.verbose_name,
            'name': self.name,
            'default': self.value()
        }
        return view.render_form_element(f, data)

class Input(FormField):
    pass

class Textarea(FormField):
    pass

class File(FormField):
    pass
