# -*- coding: utf-8 -*-

from freecritters.web import templates
from freecritters import model
from freecritters.web.form import Form, SubmitButton, HiddenField, TextField
from freecritters.web.modifiers import FormTokenValidator
from colubrid.exceptions import AccessDenied

class LogoutForm(Form):
    method = u'post'
    action = u'/logout'
    fields = [
        HiddenField(u'form_token', modifiers=[FormTokenValidator()]),
        SubmitButton(title=u'Yes', id_=u'submit')
    ]

def delete_login_cookies(response):
    response.delete_cookie('login_id')
    response.delete_cookie('response_code')
    
def logout(req):
    if req.login is None:
        raise AccessDenied()
    form = LogoutForm(req, {u'form_token': req.login.form_token()})
    if form.was_filled and not form.errors:
        req.sess.delete(req.login)
        req.login = None
        response = templates.factory.render('logged_out', req)
        delete_login_cookies(response)
        return response
    else:
        context = {u'form': form.generate()}
        return templates.factory.render('logout_form', req, context)
