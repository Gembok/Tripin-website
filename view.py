import os.path

import config
import pystache

def render(handler, filename, data, prefix=''):
	templates = os.path.join(config.ROOT, prefix, config.TEMPLATES)
	partial = pystache.render(open(os.path.join(templates, filename)).read(), data)
	full = pystache.render(open(os.path.join(templates, config.BASE_TEMPLATE)).read(), {'content': partial})
	handler.response.out.write(full)