import os.path

from google.appengine.ext.webapp import template


def render(filename, data, handler=None, prefix=''):
    path = os.path.join(os.path.dirname(__file__), 'templates', prefix, filename)
    html = template.render(path, data)
    if handler:
        handler.response.out.write(html)
    else:
        return html

def render_page(handler, filename, data):
    render(filename, data, handler)

def render_form(filename, data):
    return render(filename, data, prefix='form')