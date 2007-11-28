# -*- coding: utf-8 -*-

from freecritters import model
from freecritters.web.form import Form, TextField, IntegerModifier, \
                                  RangeValidator, SubmitButton, CheckBox, \
                                  SelectMenu, PasswordField, \
                                  RegexValidator, SameAsValidator, \
                                  Modifier, ValidationError, LengthValidator
from freecritters.web.modifiers import UsernameNotTakenValidator
from freecritters.web.login import add_login_cookies
import time

class RegisterForm(Form):
    method = u'post'
    action = 'register'
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
        raise Error403()
    form = RegisterForm(req)
    if form.was_filled and not form.errors:
        values = form.values_dict()
        # We need to find the role before creating the user because looking
        # for the role flushes the store and causes the user to be INSERTed
        # with a NULL role_id, triggering an error.
        default_role = model.Role.find_label(u'default')
        user = model.User(values['username'], values['password'])
        user.role = default_role
        model.Session.save(user)
        login = model.Login(user, None)
        model.Session.save(login)
        req.login = login
        req.user = login.user
        response = req.render_template('registered.html', username=values['username'])
        add_login_cookies(response, login)
        return response
    else:
        return req.render_template('register_form.html', form=form.generate())
