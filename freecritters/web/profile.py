# -*- coding: utf-8 -*-

from freecritters.model import User
from freecritters.web import templates
from colubrid.exceptions import PageNotFound

def profile(req, username):
    user = User.find_user(req.sess, username.decode('ascii'))
    if user is None:
        raise PageNotFound()
    context = {u'username': user.username}
    return templates.factory.render('profile', req, context)
