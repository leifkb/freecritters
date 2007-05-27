# -*- coding: utf-8 -*-

from freecritters.web import templates
from freecritters import model
from freecritters.web.form import Form, TextField, SubmitButton, PasswordField, HiddenField
from freecritters.web.modifiers import UserModifier, PasswordValidator, \
                                       SubaccountModifier
from colubrid.exceptions import AccessDenied

class LoginForm(Form):
    method = u'post'
    action = u'/login'
    fields = [
        TextField(u'user', u'Username',
                  max_length=model.User.username_length,
                  modifiers=[UserModifier()]),
        PasswordField(u'password', u'Password',
                      modifiers=[PasswordValidator(u'user', u'subaccount')]),
        TextField(u'subaccount', u'Subaccount',
                  modifiers=[SubaccountModifier(u'user')],
                  description=u"Leave this blank if you don't know what it "
                              u"is."),
        SubmitButton(title=u'Submit', id_=u'submit')
    ]

def add_login_cookies(response, login):
    response.set_cookie('login_id', login.login_id, max_age=90*24*60*60)
    response.set_cookie('login_code', login.code, max_age=90*24*60*60)
    
def login(req):
    if req.login is not None:
        raise AccessDenied()
    form = LoginForm(req)
    if form.was_filled and not form.errors:
        data = form.values_dict()
        login = model.Login(data['user'], data['subaccount'])
        req.sess.save(login)
        req.sess.flush()
        req.login = login
        req.user = login.user
        req.subaccount = login.subaccount
        context = {u'username': data['user'].username}
        response = templates.factory.render('logged_in', req, context)
        add_login_cookies(response, login)
        return response
    else:
        context = {u'form': form.generate()}
        return templates.factory.render('login_form', req, context)
    
def test(req, foo, bar):
    from colubrid import HttpResponse
    return HttpResponse('%s | %s' % (foo, bar))
