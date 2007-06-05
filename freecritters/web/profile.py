# -*- coding: utf-8 -*-

from freecritters.model import User
from colubrid.exceptions import PageNotFound

def profile(req, username):
    user = User.find_user(username.decode('ascii'))
    if user is None:
        raise PageNotFound()
    context = {
        'username': user.username,
        'profile': user.rendered_profile,
        'register_date': user.registration_date
    }
    return req.render_template('profile.html', context)