# -*- coding: utf-8 -*-

def user_link(user):
    print '--XXX--', user.unformatted_username
    return '/users/%s' % user.unformatted_username.encode('ascii')
