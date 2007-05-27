# -*- coding: utf-8 -*-

from freecritters.web import templates
from freecritters import model
from freecritters.web.form import Form, TextField, IntegerModifier, \
                                  RangeValidator, SubmitButton, CheckBox, \
                                  SelectMenu, PasswordField, \
                                  RegexValidator, SameAsValidator, \
                                  Modifier, ValidationError, LengthValidator
from freecritters.web.modifiers import UsernameNotTakenValidator
from freecritters.web.login import add_login_cookies
import time
from colubrid.exceptions import AccessDenied

class RegisterForm(Form):
    method = u'post'
    action = u'/register'
    fields = [
        TextField(u'username', u'Username',
                  max_length=model.User.username_length,
                  modifiers=[RegexValidator(model.User.username_regex,
                                            message=u'Can only contain '
                                                    u'letters, numbers, '
                                                    u'spaces, hyphens, and '
                                                    u'underscores. Can not '
                                                    u'start with a number.'),
                             UsernameNotTakenValidator()
                            ]),
        PasswordField(u'password', u'Password',
                      modifiers=[LengthValidator(3)]),
        PasswordField(u'password2', u'Re-enter Password',
                      modifiers=[SameAsValidator(u'password')]),
        SubmitButton(title=u'Submit', id_=u'submit')
    ]

def register(req):
    if req.user is not None:
        raise AccessDenied()
    form = RegisterForm(req)
    if form.was_filled and not form.errors:
        values = form.values_dict()
        user = model.User(values['username'], values['password'])
        user.role = model.Role.find_label(req.sess, u'default')
        req.sess.save(user)
        login = model.Login(user, None)
        req.sess.save(login)
        req.sess.flush()
        req.login = login
        req.user = login.user
        context = {u'username': values['username']}
        response = templates.factory.render('registered', req, context)
        add_login_cookies(response, login)
        return response
    else:
        context = {u'form': form.generate()}
        return templates.factory.render('register_form', req, context)
