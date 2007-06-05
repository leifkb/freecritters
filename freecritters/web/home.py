# -*- coding: utf-8 -*-

from freecritters.web.paginator import Paginator
from colubrid.exceptions import AccessDenied, HttpFound, PageNotFound
from freecritters.web.util import redirect

def home(req):
    return req.render_template('home.html')
