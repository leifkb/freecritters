# -*- coding: utf-8 -*-

from colubrid import HttpResponse
from freecritters.web.templates import render

@render('foo')
def foo(req, names=''):
    if names:
        names = names.split(',')
    else:
        names = []
    return {u'names': names, u'foo': req.environ}
