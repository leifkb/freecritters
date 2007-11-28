# -*- coding: utf-8 -*-

from freecritters import model
from freecritters.web.form import Form, SubmitButton, HiddenField, TextField
from freecritters.web.modifiers import FormTokenValidator

class LogoutForm(Form):
    method = u'post'
    action = 'logout'
    fields = [
        HiddenField(u'form_token', modifiers=[FormTokenValidator()]),
        SubmitButton(title=u'Yes', id_=u'submit')
    ]

def delete_login_cookies(response):
    response.delete_cookie('login_id')
    response.delete_cookie('response_code')
    
def logout(req):
    req.check_permission(None)
    if req.login is None: # HTTP Basic
        return req.render_template('cant_log_out.html')
    form = LogoutForm(req, {u'form_token': req.form_token()})
    if form.was_filled and not form.errors:
        model.Session.delete(req.login)
        req.login = None
        req.user = None
        req.subaccount = None
        response = req.render_template('logged_out.html')
        delete_login_cookies(response)
        return response
    else:
        return req.render_template('logout_form.html', form=form.generate())
