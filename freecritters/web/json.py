# -*- coding: utf-8 -*-

import simplejson
from freecritters.web.application import FreeCrittersResponse

def returns_json(fun):
    """Decorator which wraps a function's return value in a Colubrid
    HTTP response containing a JSON string.
    """
    def wrapper(*args, **kwargs):
        return FreeCrittersResponse(simplejson.dumps(fun(*args, **kwargs)),
                                    [('Content-Type', 'application/json')])
    return wrapper