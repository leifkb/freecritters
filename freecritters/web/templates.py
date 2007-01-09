# -*- coding: utf-8 -*-

from colubrid import HttpResponse
from jinja import Template, Context, EggLoader

loader = EggLoader('freecritters', 'web/templates',
                   charset='utf-8')
cache = True # Kind of ugly

# The following function is mostly stolen from Colubrid's docs.

def render(name):
    if cache:
        def proxy(f):
            t = Template(name, loader)
            def on_call(*args, **kwargs):
                result = f(*args, **kwargs)
                if isinstance(result, dict):
                    c = Context(result)
                else:
                    c = Context()
                return HttpResponse(t.render(c))
            return on_call
        return proxy
    else:
        def proxy(f):
            def on_call(*args, **kwargs):
                result = f(*args, **kwargs)
                if isinstance(result, dict):
                    c = Context(result)
                else:
                    c = Context()
                t = Template(name, loader)
                return HttpResponse(t.render(c))
            return on_call
        return proxy
