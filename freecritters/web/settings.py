# -*- coding: utf-8 -*-

from freecritters.web.form import Form, HiddenField, TextArea, SelectMenu, \
                                  SubmitButton, LengthValidator, TextField, \
                                  CheckBox, PasswordField, SameAsValidator, \
                                  BlankToNoneModifier, CheckBoxes
from freecritters.web.modifiers import FormTokenField, FormTokenValidator, HtmlModifier, \
                                       SubaccountNameNotTakenValidator, \
                                       CurrentPasswordValidator
from freecritters.model import User, Subaccount, Permission, Session
from freecritters.model.util import set_dynamic_relation
from freecritters.web.exceptions import Error403
from operator import attrgetter

edit_profile_form = Form(u'post', 'settings.edit_profile',
    FormTokenField(),
    TextArea(u'profile', u'Profile',
             modifiers=[HtmlModifier()]),
    TextArea(u'premailmessage', u'Pre-mail message',
             u'A short plain-text message which will be shown '
             u'before anyone sends you mail.',
             rows=5,
             modifiers=[
                 LengthValidator(max_len=User.pre_mail_message_max_length),
                 BlankToNoneModifier()]),
    SubmitButton(title=u'Update', id_=u'submit'))

def edit_profile(req):
    req.check_permission(u'edit_profile')
    defaults = {
        u'profile': (req.user.profile, req.user.rendered_profile),
        u'premailmessage': req.user.pre_mail_message
    }
    form = edit_profile_form(req, defaults)
    if form.successful:
        req.user.profile, req.user.rendered_profile = form[u'profile']
        req.user.pre_mail_message = form[u'premailmessage']
        updated = True
    else:
        updated = False
    return req.render_template('edit_profile.mako',
        form=form,
        updated=updated)

change_password_form = Form(u'post', 'settings.change_password',
    FormTokenField(),
    PasswordField(u'currentpassword', u'Current password',
                  modifiers=[CurrentPasswordValidator()]),
    PasswordField(u'newpassword', u'New password',
                  modifiers=[LengthValidator(3)]),
    PasswordField(u'newpassword2', u'Re-enter new password',
                  modifiers=[SameAsValidator(u'newpassword')]),
    SubmitButton(id_=u'submitbtn', title=u'Submit'))

def change_password(req):
    req.check_permission(None)
    if req.subaccount is not None:
        raise Error403()
    
    results = change_password_form(req)
    if results.successful:
        req.user.change_password(results[u'newpassword'])
        req.redirect('settings.change_password', changed=1)
    else:
        return req.render_template('change_password.mako',
            changed='changed' in req.args,
            form=results)

def permission_options(user):
    result = []
    for permission in sorted(user.role.permissions, key=attrgetter('title')):
        result.append((permission, permission.title, permission.description))
    return result
        
def subaccount_list(req):
    req.check_permission(None)
    if req.subaccount is not None:
        raise Error403()
    subaccounts = req.user.subaccounts.order_by(Subaccount.name).all()
    return req.render_template('subaccount_list.mako',
        subaccounts=subaccounts,
        deleted='deleted' in req.args,
        password_changed='password_changed' in req.args,
        created='created' in req.args)

def create_subaccount(req):
    req.check_permission(None)
    if req.subaccount is not None:
        raise Error403()
    
    form = Form(u'post', 'settings.create_subaccount',
        FormTokenField(),
        TextField(u'name', u'Name',
                  modifiers=[LengthValidator(1),
                             SubaccountNameNotTakenValidator()]),
        PasswordField(u'password', u'Password',
                      modifiers=[LengthValidator(3)]),
        PasswordField(u'password2', u'Re-enter Password',
                      modifiers=[SameAsValidator(u'password')]),
        CheckBoxes(u'permissions', u'Permissions', options=permission_options(req.user)),
        SubmitButton(title=u'Submit', id_=u'submit'),
        reliable_field=u'form_token')
    
    results = form(req)
    if results.successful:
        subaccount = Subaccount(req.user, results[u'name'], results[u'password'])
        Session.save(subaccount)
        subaccount.permissions = resuts[u'permissions']
        req.redirect('settings.subaccount_list', created=1)
    else:
        return req.render_template('create_subaccount.mako',
            form=results)
        
def edit_subaccount(req, subaccount_id):
    req.check_permission(None)
    if req.subaccount is not None:
        raise Error403()
    
    subaccount = Subaccount.query.get(subaccount_id)
    if subaccount is None:
        return None
    if subaccount.user != req.user:
        raise Error403()
        
    form = Form(u'post', ('settings.edit_subaccount', dict(subaccount_id=subaccount_id)),
        FormTokenField(),
        CheckBoxes(u'permissions', u'Permissions', options=permission_options(req.user)),
        SubmitButton(id_=u'submitbtn', title=u'Submit'),
        reliable_field=u'form_token')
    
    
    defaults = {u'permissions': list(subaccount.permissions)}
    
    results = form(req, defaults)
    if results.successful:
        subaccount.permissions = results[u'permissions']
        updated = True
    else:
        updated = False
    return req.render_template('edit_subaccount.mako',
        form=results,
        updated=updated,
        subaccount=subaccount)
    
subaccount_delete_form = Form(u'post', None,
    FormTokenField(),
    SubmitButton(title=u'Yes', id_=u'submit'))
    
def delete_subaccount(req, subaccount_id):
    req.check_permission(None)
    if req.subaccount is not None:
        raise Error403()
    
    subaccount = Subaccount.query.get(subaccount_id)
    if subaccount is None:
        return None
    if subaccount.user != req.user:
        raise Error403()
        
    form = subaccount_delete_form(req)
    form.action = 'settings.delete_subaccount', dict(subaccount_id=subaccount_id)
    
    if form.successful:
        Session.delete(subaccount)
        req.redirect('settings.subaccount_list', deleted=1)
    else:
        return req.render_template('delete_subaccount.mako',
            form=form,
            subaccount=subaccount)

subaccount_password_change_form = Form(u'post', None,
    FormTokenField(),
    PasswordField(u'account_password', u'Account password',
                  u'The current password to your account '
                  u'(not to the subaccount).',
                  modifiers=[CurrentPasswordValidator()]),
    PasswordField(u'new_password', u'New password',
                  modifiers=[LengthValidator(3)]),
    PasswordField(u'new_password2', u'Re-enter new password',
                  modifiers=[SameAsValidator(u'new_password')]),
    SubmitButton(title=u'Submit', id_=u'submit'))
    
def change_subaccount_password(req, subaccount_id):
    req.check_permission(None)
    if req.subaccount is not None:
        raise Error403
        
    subaccount = Subaccount.query.get(subaccount_id)
    if subaccount is None:
        return None
    if subaccount.user != req.user:
        raise Error403()
        
    form = subaccount_password_change_form(req)
    form.action = 'settings.change_subaccount_password', dict(subaccount_id=subaccount.subaccount_id)
    
    if form.successful:
        subaccount.change_password(form[u'new_password'])
        req.redirect('settings.subaccount_list', password_changed=1)
    else:
        return req.render_template('change_subaccount_password.mako',
            form=form,
            subaccount=subaccount)
