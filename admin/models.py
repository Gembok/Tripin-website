import form
import front.models
import view

class AdminModel:
    model = None
    edit = []
    show = []
    
    def __init__(self, id=None):
        self.id = id
        self.instance = None
        self.get_instance()
    
    def make_form(self, post_data={}, upload_url=None):
        self.form = form.Form(self, self.get_edit_fields(), dict(post_data), upload_url)
        self.form.make_fields()
        self.check_references()
    
    def get_instance(self):
        """Get old instance or new empty one."""
        if self.id and not self.instance:
            self.instance = self.model.get_by_id(self.id)
        else:
            self.instance = self.model()
    
    def get_edit_fields(self):
        edit_fields = []
        base_fields = self.model.properties()
        for name in self.edit:
            try:
                edit_fields.append((name, base_fields[name]))
            except KeyError: pass
        return edit_fields
    
    def check_references(self):
        """Add reference list field if the model has references"""
        for key, model in registered.iteritems():
            collection = '%s_set' % model.__name__.lower()
            try:
                refs = getattr(self.instance, collection)
                self.form.add_ref(key, refs)
            except AttributeError: pass
    
    def set(self, name, value):
        setattr(self.instance, name, value)
    
    def get_by_id(self):
        return self.model.get_by_id(self.id)
    
    def save(self):
        if self.form.validate():
            return self.instance.put()
        else:
            return False
    
    def delete(self):
        return self.instance.delete()
    
    def render(self):
        return {
            'form': self.form.render_form(),
            'files':self.form.render_files()
        }

# User classes
class Member(AdminModel):
	model = front.models.Member
	show = ['name', 'bio', 'image', 'one', 'email', 'link', 'files']
	edit = show


class Concert(AdminModel):
    model = front.models.Concert
    show = ['title', 'member']
    edit = show

registered = {'member': Member, 'concert': Concert}