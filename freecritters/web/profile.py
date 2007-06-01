# -*- coding: utf-8 -*-

from freecritters.model import User
from freecritters.web import templates
from colubrid.exceptions import PageNotFound

def profile(req, username):
    user = User.find_user(username.decode('ascii'))
    if user is None:
        raise PageNotFound()
    context = {u'username': user.username, u'profile': user.rendered_profile,
               u'register_date': user.registration_date}
    return templates.factory.render('profile', req, context)
