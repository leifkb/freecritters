# -*- coding: utf-8 -*-

from freecritters.web.form import Form, HiddenField, TextArea, SelectMenu, \
                                  SubmitButton, LengthValidator, TextField, \
                                  CheckBox, PasswordField, SameAsValidator, \
                                  BlankToNoneModifier
from freecritters.web.modifiers import FormTokenField, FormTokenValidator, HtmlModifier, \
                                       SubaccountNameNotTakenValidator, \
                                       CurrentPasswordValidator
from freecritters.model import User, Subaccount, Permission, Session
from freecritters.web.exceptions import Error403

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

def add_subaccount_permission_fields(form, user):
    for permission in user.role.permissions:
        form.add_field(CheckBox(
            u'perm' + unicode(permission.permission_id),
            permission.title,
            permission.description
        ))
        
def permissions_from_results(results):
    for key in results:
        if key.startswith(u'perm'):
            try:
                perm_id = int(key[4:])
            except ValueError:
                continue
            if results[key]:
                yield Permission.query.get(perm_id)
    
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
        reliable_field=u'form_token')
    add_subaccount_permission_fields(form, req.user)
    form.add_field(SubmitButton(title=u'Submit', id_=u'submit'))
    
    results = form(req)
    if results.successful:
        subaccount = Subaccount(req.user, results[u'name'], results[u'password'])
        Session.save(subaccount)
        for permission in permissions_from_results(results):
            subaccount.permissions.append(permission)
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
        
    form = Form(u'post', ('settings.edit_subaccount', dict(subaccount_id=subaccount_id)),
        FormTokenField(),
        reliable_field=u'form_token')
    add_subaccount_permission_fields(form, req.user)
    form.add_field(SubmitButton(title=u'Submit', id_=u'submit'))

    defaults = {}
    for permission in subaccount.permissions:
        defaults[u'perm%s' % permission.permission_id] = True
    
    results = form(req, defaults)
    if results.successful:
        current_perms = set(subaccount.permissions)
        selected_perms = set(permissions_from_results(results))
        deleted_perms = current_perms - selected_perms
        added_perms = selected_perms - current_perms
        for deleted_perm in deleted_perms:
            subaccount.permissions.remove(deleted_perm)
        for added_perm in added_perms:
            subaccount.permissions.append(added_perm)
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
    
    subaccount = req.user.subaccounts.get(subaccount_id)
    if subaccount is None:
        return None
        
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
        
    form = subaccount_password_change_form(req)
    form.action = 'settings.change_subaccount_password', dict(subaccount_id=subaccount.subaccount_id)
    
    if form.successful:
        subaccount.change_password(form[u'new_password'])
        req.redirect('settings.subaccount_list', password_changed=1)
    else:
        return req.render_template('change_subaccount_password.mako',
            form=form,
            subaccount=subaccount)
