# -*- coding: utf-8 -*-

from freecritters import model
from freecritters.web.form import Form, SubmitButton, HiddenField, TextField
from freecritters.web.modifiers import FormTokenField
from freecritters.web.util import confirm

def delete_login_cookies(response):
    response.delete_cookie('login_id')
    response.delete_cookie('response_code')
    
def logout(req):
    req.check_permission(None)
    if req.login is None: # HTTP Basic
        return req.render_template('cant_log_out.mako')
    
    confirm(u'log out')
    
    model.Session.delete(req.login)
    req.login = None
    req.user = None
    req.subaccount = None
    response = req.render_template('logged_out.mako')
    delete_login_cookies(response)
    return response