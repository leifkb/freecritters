# -*- coding: utf-8 -*-

import simplejson
from colubrid import HttpResponse

def returns_json(fun):
    def wrapper(*args, **kwargs):
        return HttpResponse(simplejson.dumps(fun(*args, **kwargs)),
                            [('Content-Type', 'application/json')])
    return wrapper
