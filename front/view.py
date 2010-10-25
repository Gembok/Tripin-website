import os.path

import pystache

front = os.path.abspath(os.path.dirname(__file__))
templates = os.path.join(front, 'templates')

def render(handler, filename, data):
    html = render_partial(os.path.join(templates, filename), data)
    handler.response.out.write(html)

def render_full(handler, filename, data, prefix=''):
	folder = os.path.join(templates, prefix)
	partial = render_partial(os.path.join(folder, filename), data)
	full = pystache.render(open(os.path.join(templates, 'base.html')).read(), {'content': partial})
	handler.response.out.write(full)

def render_partial(filename, data):
    try:
        return pystache.render(open(filename).read(), data)
    except Exception, e:
        print e