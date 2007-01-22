# -*- coding: utf-8 -*-

from freecritters.web import templates

def home(req):
    return templates.factory.render('home', req)
