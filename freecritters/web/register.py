# -*- coding: utf-8 -*-

from freecritters.model import Session, User, Role, Login
from freecritters.web.form import Form, TextField, IntegerModifier, \
                                  RangeValidator, SubmitButton, CheckBox, \
                                  SelectMenu, PasswordField, \
                                  RegexValidator, SameAsValidator, \
                                  Modifier, ValidationError, LengthValidator
from freecritters.web.modifiers import UsernameNotTakenValidator
from freecritters.web.login import add_login_cookies
from freecritters.web.exceptions import Error403
import time

register_form = Form(u'post', 'register',
    TextField(u'username', u'Username',
              max_length=User.username_length,
              modifiers=[RegexValidator(User.username_regex,
                                        message=u'Can only contain '
                                                u'letters, numbers, '
                                                u'spaces, hyphens, and '
                                                u'underscores. Can not '
                                                u'start with a number.'),
                         UsernameNotTakenValidator()]),
    PasswordField(u'password', u'Password',
                  modifiers=[LengthValidator(3)]),
    PasswordField(u'password2', u'Re-enter Password',
                  modifiers=[SameAsValidator(u'password')]),
    SubmitButton(title=u'Submit', id_=u'submit'))

def register(req):
    if req.user is not None:
        raise Error403()
    results = register_form(req)
    if results.successful:
        # We need to find the role before creating the user because looking
        # for the role flushes the session and causes the user to be INSERTed
        # with a NULL role_id, triggering an error.
        default_role = Role.find_label(u'default')
        user = User(results['username'], results['password'])
        user.role = default_role
        Session.save(user)
        login = Login(user, None)
        Session.save(login)
        req.login = login
        req.user = login.user
        response = req.render_template('registered.mako')
        add_login_cookies(response, login)
        return response
    else:
        return req.render_template('register_form.mako',
            form=results)
