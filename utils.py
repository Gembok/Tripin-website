import datetime
import time

from google.appengine.ext import db, blobstore
from google.appengine.api import images

from front import models


def to_dict(model):
    data = {}
    for key, value in model.properties().iteritems():
        val = value.get_value_for_datastore(model)
        if isinstance(val, datetime.datetime):
            val = time.mktime(val.utctimetuple())
        elif isinstance(val, db.Model):
            val = to_dict(val)
        elif isinstance(val, (blobstore.BlobKey, db.Key)):
            val = str(val)
        data[key] = val
        try:
            data['id'] = model.key().id()
        except Exception, e:
            print e
        data['key'] = str(model.key())
    return data

def to_dicts(models):
    data = []
    for model in models:
        data.append(to_dict(model))
    return data

def to_dicts_list(models, keys):
    data = []
    dicts = to_dicts(models)
    for d in dicts:
        it = d
        it.update({'fields': []})
        for key in keys:
            it['fields'].append(d[key])
        data.append(it)
    return data

# def serving_url(val, size, crop):
#     info = blobstore.BlobInfo.get(val)
#     try:
#         info.content_type.index('image')
#         return images.get_serving_url(str(val), size, crop)
#     except ValueError:
#         return '/serve/%s' % str(val)