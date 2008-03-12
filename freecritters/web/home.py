# -*- coding: utf-8 -*-

from freecritters.web.util import confirm

def home(req):
    return req.render_template('home.mako')