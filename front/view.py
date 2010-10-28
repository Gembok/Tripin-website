import os.path

import pystache

front = os.path.abspath(os.path.dirname(__file__))
templates = os.path.join(front, 'templates')

def render(handler, filename, data):
    html = render_partial(filename, data)
    handler.response.out.write(html)

def render_full(handler, filename, data, prefix=''):
	fullfile = os.path.join(prefix, filename)
	partial = render_partial(filename, data)
	full = pystache.render(get_file('base.html'), {'content': partial})
	handler.response.out.write(full)

def render_partial(filename, data):
    try:
        return pystache.render(get_file(filename), data)
    except Exception, e:
        print e

def get_file(filename):
    return open(os.path.join(templates, filename)).read()
