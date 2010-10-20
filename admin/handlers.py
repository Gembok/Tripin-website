import datetime
import urllib

from google.appengine.ext import webapp
from google.appengine.ext import db, blobstore
from google.appengine.ext.webapp import blobstore_handlers

import front
import models
import view


class AdminHandler(blobstore_handlers.BlobstoreUploadHandler):
    def to_dict(self, model):
        data = {}
        for key, value in model.properties().iteritems():
            val = value.get_value_for_datastore(model)
            if isinstance(val, datetime.datetime):
                ms = time.mktime(val.utctimetuple()) * 1000
                ms += getattr(val, 'microseconds', 0) / 1000
                val = int(ms)
            elif isinstance(val, db.Model):
                val = self.to_dict(val)
            data[key] = val
            try:
                data['id'] = model.key().id()
            except:
                pass
        return data
    
    def to_dicts(self, models):
        data = []
        for model in models:
            data.append(self.to_dict(model))
        return data
    
    def id(self):
        return int(self.request.get('id', 0))
    
    def get_url(self):
        return '%s?%s' % (self.request.path, self.request.query_string)
    
    def get_model(self, model, **kw):
        return models.registered.get(model, models.AdminModel)(**kw)  #TODO:check if model exists
    
    def render(self, filename, data):
        view.render_page(self, filename, data)


class ModelsHandler(AdminHandler):
    def get(self):
        names = [{'name': k} for k, v in models.registered.iteritems()]
        data = {'models': names}
        self.render('models.html', data)


class ListHandler(AdminHandler):
    def get(self, model):
        adminmodel = self.get_model(model)
        items = adminmodel.model.all().fetch(10)
        dicts = self.to_dicts(items)
        data = {
            'model': model,
            'fields': [{'name': i} for i in adminmodel.show],
            'items': dicts
        }
        self.render('list.html', data)


class EditHandler(AdminHandler):
    def get(self, model):
        id = self.id()
        adminmodel = self.get_model(model, id=id, url=self.get_url())
        data = {
            'form': adminmodel.render_form()
        }
        self.render('edit.html', data)
    
    def post(self, model):
        id = self.id()
        print 'post() requested'
        print self.request.POST
        adminmodel = self.get_model(model, id=id, data=self.request.POST, url=self.get_url())
        if adminmodel.validate():
            key = adminmodel.save()
            self.redirect('/admin/list/%s' % model)
        else:
            self.response.out.write(adminmodel.errors())
            data = {
                'form': adminmodel.render_form()
            }
            self.render('edit.html', data)


class DeleteHandler(AdminHandler):
    def get(self, model):
        id = self.id()
        confirm = int(self.request.get('confirm', 0))
        if not confirm:
            self.response.out.write('<a href="?id=%d&confirm=1">Confirm</a> - <a href="/admin/list/%s">Cancel</a>' % (id, model))
        else:
            admin_model = self.get_model(model, id=id)
            admin_model.delete()
            self.redirect('/admin/list/%s' % model)