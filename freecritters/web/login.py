# -*- coding: utf-8 -*-

from freecritters import model
from freecritters.web.form import Form, TextField, SubmitButton, PasswordField, HiddenField
from freecritters.web.modifiers import UserModifier, PasswordValidator, \
                                       SubaccountModifier
from freecritters.web.exceptions import Error403
from datetime import datetime, timedelta

class LoginForm(Form):
    method = u'post'
    action = 'login'
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
    max_age = 90*24*60*60 # 90 days
    expires = datetime.utcnow() + timedelta(seconds=max_age)
    response.set_cookie('login_id', login.login_id, max_age=max_age, expires=expires)
    response.set_cookie('login_code', login.code, max_age=max_age, expires=expires)
    
def login(req):
    if req.login is not None:
        raise Error403()
    form = LoginForm(req)
    if form.was_filled and not form.errors:
        data = form.values_dict()
        login = model.Login(data['user'], data['subaccount'])
        model.Session.save(login)
        req.login = login
        req.user = login.user
        req.subaccount = login.subaccount
        response = req.render_template('logged_in.html', username=data['user'].username)
        add_login_cookies(response, login)
        return response
    else:
        return req.render_template('login_form.html', form=form.generate())