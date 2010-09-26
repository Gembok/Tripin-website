from google.appengine.ext import webapp

import models
import view
from forms import Form

class AdminHandler(webapp.RequestHandler):
    def to_dict(self, model):
        data = {}
        for key, value in model.properties().iteritems():
            val = value.get_value_for_datastore(model)
            if isinstance(val, datetime.datetime):
                ms = time.mktime(val.utctimetuple()) * 1000
                ms += getattr(value, 'microseconds', 0) / 1000
                val = int(ms)
            elif isinstance(val, db.Model):
                val = self.to_dict(val)
                data[key] = val
                return data
    
    def render(self, filename, data):
        view.render(self, filename, data, 'admin')

class ModelsHandler(AdminHandler):
    def get(self):
        names = [{'name': k} for k, v in models.registered.iteritems()]
        data = {'models': names}
        self.render('models.html', data)

class ListHandler(AdminHandler):
    def get(self, model):
        m = models.registered.get(model, None)
        values = m.model.all().fetch(10)
        data = {
            'model': model,
            'fields': [{'name': i} for i in m.show],
            'values': [{'key': i.key()} for i in values]
        }
        self.render('list.html', data)

class EditHandler(AdminHandler):
    def get(self, model):
        id = int(self.request.get('_id', 0))
        if id:
            instance = adminmodel.model.get(db.Key.from_path(adminmodel.model.kind(), id))
        else:
            instance = None
        form = models.registered.get(model, None)(instance=instance)
        data = {
            'form': form.render(),
            '_id': id
        }
        self.render('edit.html', data)
    
    def post(self, model):
        id = int(self.request.get('_id', 0))
        adminmodel = models.registered.get(model, None)
        if id:
            item = adminmodel.model.get(db.Key.from_path(adminmodel.model.kind(), id))
        else:
            item = adminmodel.model()
        

class DeleteHandler(AdminHandler):
    def get(self):
        pass
