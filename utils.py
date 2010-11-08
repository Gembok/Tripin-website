import datetime
import time

import markdown2
from google.appengine.ext import db, blobstore
from google.appengine.api import images

from front import models


def to_dict(model):
    data = {}
    for key, value in model.properties().iteritems():
        val = value.get_value_for_datastore(model)
        if isinstance(val, datetime.datetime):
            val = time.mktime(val.utctimetuple())
        elif isinstance(val, db.Text):
            val = markdown2.markdown(val)
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
