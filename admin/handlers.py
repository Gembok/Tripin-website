import urllib
import logging

from google.appengine.ext import webapp
from google.appengine.ext import db, blobstore
from google.appengine.ext.webapp import blobstore_handlers

import utils
import front
import models
import view

DEFAULT = 'biographie'

class AdminHandler(blobstore_handlers.BlobstoreUploadHandler):
    def id(self):
        return int(self.request.get('id', 0) or 0)
    
    def upload_url(self, model):
        return '/admin/upload/%s/?%s' % (model, self.request.query_string)
    
    def get_model(self, model, **kw):
        return models.registered.get(model, models.AdminModel)(name=model, **kw)  #TODO:check if model exists
    
    def get_model_list(self):
        return models.registered.keys()
    
    def render(self, filename, data, model):
        data.update({
            'model': model,
            'menu': self.get_model_list()
        })
        view.render_page(self, filename, data)


class ListHandler(AdminHandler):
    def get(self, model=None):
        if not model:
            model = DEFAULT
        adminmodel = self.get_model(model)
        items = adminmodel.model.all().fetch(10)
        self.render('list.html', {
            'fields': [{'name': i} for i in adminmodel.show],
            'items': utils.to_dicts_list(items, adminmodel.show)
        }, model)


class EditHandler(AdminHandler):
    def get(self, model):
        id = self.id()
        parent = self.request.get('parent', '')
        parent_id = self.request.get('parent_id', '')
        adminmodel = self.get_model(model, id=id)
        adminmodel.make_form(upload_url = self.upload_url(model))
        forms = adminmodel.render()
        self.render('edit.html', {
            'parent': parent,
            'parent_id': parent_id,
            'form': forms['form'],
            'files': forms['files']
        }, model)
    
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
                'parent': parent,
                'parent_id': parent_id,
                'form': forms['form'],
                'files': forms['files']
            }, model)


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
            admin_model.make_form()
            admin_model.delete()
            self.redirect('/admin/list/%s' % model)

routes = [
    (r'^/admin/edit/(\w+)/?$', EditHandler),
    (r'^/admin/delete/(\w+)/?$', DeleteHandler),
    (r'^/admin/upload/(\w+)/?$', UploadHandler),
    (r'^/admin/deleteblob/(\w+)/?$', DeleteBlobHandler),
    (r'^/admin/list/(\w+)/?$', ListHandler),
    (r'^/admin/?', ListHandler)
]