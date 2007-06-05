# -*- coding: utf-8 -*-

from freecritters.web.form import Form, HiddenField, TextArea, SelectMenu, \
                                  SubmitButton, LengthValidator, TextField, \
                                  CheckBox, PasswordField, SameAsValidator
from freecritters.web.modifiers import FormTokenValidator, HtmlModifier, \
                                       SubaccountNameNotTakenValidator, \
                                       CurrentPasswordValidator
from freecritters.model import User, Subaccount
from freecritters.web.util import redirect
from sqlalchemy import Query
from colubrid.exceptions import AccessDenied, HttpFound, PageNotFound

class EditProfileForm(Form):
    method = u'post'
    action = u'/editprofile'
    fields = [
        HiddenField(u'form_token', modifiers=[FormTokenValidator()]),
        TextArea(u'profile', u'Profile',
                 modifiers=[HtmlModifier()]),
        TextArea(u'premailmessage', u'Pre-mail message',
                 u'A short plain-text message which will be shown '
                 u'before anyone sends you mail.',
                 rows=5,
                 modifiers=[LengthValidator( \
                     max_len=User.pre_mail_message_max_length)]),
        SubmitButton(title=u'Update', id_=u'submit')
    ]

def edit_profile(req):
    req.check_permission(u'edit_profile')
    defaults = {
        u'form_token': req.form_token(),
        u'profile': (req.user.profile, req.user.rendered_profile)
    }
    if req.user.pre_mail_message is not None:
        defaults['premailmessage'] = req.user.pre_mail_message
    form = EditProfileForm(req, defaults)
    context = {'form': form.generate()}
    if form.was_filled and not form.errors:
        values = form.values_dict()
        req.user.profile = values[u'profile'][0]
        req.user.rendered_profile = values[u'profile'][1]
        if values[u'premailmessage'].isspace() or not values[u'premailmessage']:
            req.user.pre_mail_message = None
        else:
            req.user.pre_mail_message = values['premailmessage']
        context['updated'] = True
    return req.render_template('edit_profile.html', context)

def subaccount_permission_fields(user):
    fields = []
    for permission in user.role.permissions:
        fields.append(CheckBox(
            u'perm' + unicode(permission.permission_id),
            permission.title,
            permission.description
        ))
    return fields

def permissions_from_values(req, values):
    permissions = []
    for permission in req.user.role.permissions:
        if values[u'perm' + unicode(permission.permission_id)]:
            permissions.append(permission)
    return permissions
    
def subaccount_list(req):
    req.check_permission(None)
    if req.subaccount is not None:
        raise AccessDenied()
    subaccounts = []
    for subaccount in req.user.subaccounts:
        subaccounts.append({
            'id': subaccount.subaccount_id,
            'name': subaccount.name
        })
    context = {
        'subaccounts': subaccounts
    }
    for arg in ['deleted', 'password_changed', 'created']:
        if arg in req.args:
            context[arg] = True
    return req.render_template('subaccount_list.html', context)

def create_subaccount(req):
    req.check_permission(None)
    if req.subaccount is not None:
        raise AccessDenied()
        
    class CreateSubaccountForm(Form):
        method = u'post'
        action = u'/subaccounts/create'
        fields = [
            HiddenField(u'form_token', modifiers=[FormTokenValidator()]),
            TextField(u'name', u'Name',
                      modifiers=[LengthValidator(1),
                                 SubaccountNameNotTakenValidator()]),
            PasswordField(u'password', u'Password',
                          modifiers=[LengthValidator(3)]),
            PasswordField(u'password2', u'Re-enter Password',
                          modifiers=[SameAsValidator(u'password')])
        ]
        fields += subaccount_permission_fields(req.user)
        fields.append(SubmitButton(title=u'Submit', id_=u'submit'))
    
    form = CreateSubaccountForm(req, {u'form_token': req.form_token()})
    if form.was_filled and not form.errors:
        values = form.values_dict()
        subaccount = Subaccount(req.user, values['name'],
                                values['password'])
        subaccount.permissions = permissions_from_values(req, values)
        redirect(req, HttpFound, '/subaccounts?created=1')
    else:
        context = {u'form': form.generate()}
        return req.render_template('create_subaccount.html', context)
        
def edit_subaccount(req, subaccount_id):
    req.check_permission(None)
    if req.subaccount is not None:
        raise AccessDenied()
    subaccount = Query(Subaccount).get(subaccount_id)
    if subaccount is None:
        raise PageNotFound()
        
    class EditSubaccountForm(Form):
        method = u'post'
        action = u'/subaccounts/%s/edit' % subaccount_id
        reliable_field = u'form_token'
        fields = [
            HiddenField(u'form_token', modifiers=[FormTokenValidator()])
        ]
        fields += subaccount_permission_fields(req.user)
        fields.append(SubmitButton(title=u'Submit', id_=u'submit'))
    
    defaults = {u'form_token': req.form_token()}
    for permission in subaccount.permissions:
        defaults[u'perm' + unicode(permission.permission_id)] = True
    form = EditSubaccountForm(req, defaults)
    if form.was_filled and not form.errors:
        values = form.values_dict()
        subaccount.permissions = permissions_from_values(req, values)
        context = {'updated': True}
    else:
        context = {'updated': False}
    context['form'] = form.generate()
    context['subaccount_name'] = subaccount.name
    return req.render_template('edit_subaccount.html', context)
    
class SubaccountDeleteForm(Form):
    method = u'post'
    fields = [
        HiddenField(u'form_token', modifiers=[FormTokenValidator()]),
        SubmitButton(title=u'Yes', id_=u'submit')
    ]
    
def delete_subaccount(req, subaccount_id):
    req.check_permission(None)
    if req.subaccount is not None:
        raise AccessDenied()
    subaccount = Query(Subaccount).get(subaccount_id)
    if subaccount is None:
        raise PageNotFound()
        
    form = SubaccountDeleteForm(req, {u'form_token': req.form_token()})
    form.action = '/subaccounts/%s/delete' % subaccount.subaccount_id
    if form.was_filled and not form.errors:
        req.sess.delete(subaccount)
        redirect(req, HttpFound, '/subaccounts?deleted=1')
    else:
        context = {
            u'form': form.generate(),
            u'name': subaccount.name
        }
        return req.render_template('delete_subaccount.html', context)
        
class SubaccountPasswordChangeForm(Form):
    method = u'post'
    fields = [
        HiddenField(u'form_token', modifiers=[FormTokenValidator()]),
        PasswordField(u'account_password', u'Account password',
                      u'The current password to your account '
                      u'(not to the subaccount).',
                      modifiers=[CurrentPasswordValidator()]),
        PasswordField(u'new_password', u'New password',
                      modifiers=[LengthValidator(3)]),
        PasswordField(u'new_password2', u'Re-enter new password',
                      modifiers=[SameAsValidator(u'new_password')]),
        SubmitButton(title=u'Submit', id_=u'submit')
    ]
    
def change_subaccount_password(req, subaccount_id):
    req.check_permission(None)
    if req.subaccount is not None:
        raise AccessDenied()
        
    subaccount = Query(Subaccount).get(subaccount_id)
    if subaccount is None:
        raise PageNotFound()
    
    defaults = {
        u'form_token': req.form_token()
    }
        
    form = SubaccountPasswordChangeForm(req, defaults)
    form.action = '/subaccounts/%s/change_password' % subaccount.subaccount_id
    
    if form.was_filled and not form.errors:
        values = form.values_dict()
        subaccount.change_password(values[u'new_password'])
        redirect(req, HttpFound, u'/subaccounts?password_changed=1')
    else:
        context = {
            'form': form.generate(),
            'name': subaccount.name
        }
        return req.render_template('change_subaccount_password.html', context)
