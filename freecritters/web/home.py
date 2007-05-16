# -*- coding: utf-8 -*-

from freecritters.web import templates
from freecritters.web.paginator import Paginator
from colubrid.exceptions import AccessDenied, HttpFound, PageNotFound
from freecritters.web.util import redirect

def home(req):
    return templates.factory.render('home', req)
