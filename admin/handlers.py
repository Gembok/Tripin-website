import urllib
import logging

from google.appengine.ext import webapp
from google.appengine.ext import db, blobstore
from google.appengine.ext.webapp import blobstore_handlers

import utils
import front
import models
import view

webapp.template.register_template_library('django_hack')

class AdminHandler(blobstore_handlers.BlobstoreUploadHandler):
    def id(self):
        return int(self.request.get('id', 0))
    
    def upload_url(self, model):
        return '/admin/upload/%s/?%s' % (model, self.request.query_string)
    
    def get_model(self, model, **kw):
        return models.registered.get(model, models.AdminModel)(name=model, **kw)  #TODO:check if model exists
    
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
        data = {
            'model': model,
            'fields': [{'name': i} for i in adminmodel.show],
            'items': utils.to_dicts_list(items, adminmodel.show)
        }
        self.render('list.html', data)


class EditHandler(AdminHandler):
    def get(self, model):
        id = self.id()
        parent = self.request.get('parent', '')
        parent_id = self.request.get('parent_id', '')
        adminmodel = self.get_model(model, id=id)
        adminmodel.make_form(upload_url = self.upload_url(model))
        forms = adminmodel.render()
        self.render('edit.html', data = {
            'model': model,
            'parent': parent,
            'parent_id': parent_id,
            'form': forms['form'],
            'files': forms['files']
        })
    
    def post(self, model):
        id = self.id()
        adminmodel = self.get_model(model, id=id)
        adminmodel.make_form(post_data=self.request.POST, upload_url=self.upload_url(model))
        id_saved = adminmodel.save()
        if id_saved:
            self.redirect('/admin/edit/%s/?id=%d' % (model, id_saved.id()))
        else:
            parent_id = self.request.get('parent_id', '')
            parent = self.request.get('parent', '')
            forms = adminmodel.render()
            self.render('edit.html', {
                'model': model,
                'parent': parent,
                'parent_id': parent_id,
                'form': forms['form'],
                'files': forms['files']
            })


class UploadHandler(AdminHandler):
    def post(self, model):
        id = self.id()
        adminmodel = self.get_model(model, id=id)
        adminmodel.make_form()
        adminmodel.upload(self)
        self.redirect('/admin/edit/%s?id=%d' % (model, id))


class DeleteBlobHandler(AdminHandler):
    def get(self, model):
        id = self.id()
        key = self.request.get('key', None)
        adminmodel = self.get_model(model, id=id)
        adminmodel.make_form()
        adminmodel.delete_blob(key)
        self.redirect('/admin/edit/%s?id=%d' % (model, id))


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
