# -*- coding: utf-8 -*-

from freecritters.model import User

def profile(req, username):
    user = User.find_user(username)
    if user is None:
        return None
    return req.render_template('profile.mako', user=user)