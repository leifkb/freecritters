# -*- coding: utf-8 -*-

def groups(req):
    req.check_permission(None) # XXX
    return req.render_template('groups.html')