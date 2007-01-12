# -*- coding: utf-8 -*-

from colubrid import HttpResponse
from jinja import Template, Context, EggLoader

loader = EggLoader('freecritters', 'web/templates',
                   charset='utf-8')
cache = True # This is modified in run.py; kind of ugly

# The following function is partially stolen from Colubrid's docs.

def render(name):
    def proxy(f):
        if cache:
            t = Template(name, loader)
        else:
            t = None
        def on_call(req, *args, **kwargs):
            result = f(req, *args, **kwargs)
            globalcontext = {'fc': {'config': req.config}}
            if isinstance(result, dict):
                globalcontext.update(result)
            c = Context(globalcontext)
            if t is None: # Ugly, but better than code duplication
                t2 = Template(name, loader)
            else:
                t2 = t
            return HttpResponse(t2.render(c))
        return on_call
    return proxy
