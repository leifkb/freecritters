# -*- coding: utf-8 -*-

from freecritters.web import templates
from freecritters.web.paginator import Paginator

def home(req):
    paginator = Paginator(req, 1000)
    return templates.factory.render('home', req, {u'foo': paginator.__dict__})
