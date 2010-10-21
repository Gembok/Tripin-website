import datetime

from google.appengine.ext import db, blobstore

def to_dict(model):
    data = {}
    for key, value in model.properties().iteritems():
        val = value.get_value_for_datastore(model)
        if isinstance(val, datetime.datetime):
            ms = time.mktime(val.utctimetuple()) * 1000
            ms += getattr(val, 'microseconds', 0) / 1000
            val = int(ms)
        elif isinstance(val, db.Model):
            val = to_dict(val)
        data[key] = val
        try:
            data['id'] = model.key().id()
        except Exception, e:
            print e
        data['key'] = model.key()
    return data

def to_dicts(models):
    data = []
    for model in models:
        data.append(to_dict(model))
    return data