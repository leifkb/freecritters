# -*- coding: utf-8 -*-

from freecritters.web.templates import render
from freecritters import model
from freecritters.web.form import Form, TextField, IntegerModifier, \
                                  RangeValidator, SubmitButton, CheckBox, \
                                  SelectMenu, PasswordField, SameAsValidator
import time

class FooForm(Form):
    method = u'post'
    action = u''
    fields = [
        TextField(u'name', u'Name', description=u'Your name.'),
        TextField(u'age', u'Age', modifiers=[IntegerModifier(),
                                             RangeValidator(1, 130)],
                  description=u'Your age.'),
        SelectMenu(u'gender', u'Gender', options=[(u'male', u'Male'),
                                                  (u'female', u'Female')]),
        CheckBox(u'alive', u'Alive'),
        PasswordField(u'password', u'Password'),
        PasswordField(u'password2', u'Re-enter Password',
                      modifiers=[SameAsValidator(u'password')]),
        SubmitButton(title=u'Submit', id_=u'submit')
    ]

@render('foo')
def foo_render(req, form):
    return {u'bar': form}

@render('bar')
def bar_render(req, data):
    return {u'data': data}
    
def foo(req):
    foof = FooForm(req, {})
    if foof.was_filled and not foof.errors:
        return bar_render(req, foof.values_dict())
    else:
        return foo_render(req, foof.generate())
    
@render('foo')
def foo2(req):
    if 'add' in req.form:
        m = model.Message()
        m.message = req.form['add']
        req.sess.save(m)
        
    for msg_id in req.form.getlist('del'):
        try:
            msg_id = int(msg_id)
        except ValueError:
            continue
        msg = req.sess.query(model.Message).get(msg_id)
        if msg is not None:
            req.sess.delete(msg)
    
    req.sess.flush()
    
    messages = req.sess.query(model.Message).select()
    return {u'messages': messages, u'environ': req.__dict__}
