# -*- coding: utf-8 -*-

from freecritters.web.form import Form, HiddenField, TextArea, SelectMenu, \
                                  SubmitButton, LengthValidator, TextField, \
                                  CheckBox, PasswordField, SameAsValidator, \
                                  BlankToNoneModifier
from freecritters.web.modifiers import FormTokenValidator, HtmlModifier, \
                                       SubaccountNameNotTakenValidator, \
                                       CurrentPasswordValidator
from freecritters.model import User, Subaccount, Permission, Session
from freecritters.web.exceptions import Error403

class EditProfileForm(Form):
    method = u'post'
    action = 'settings.edit_profile'
    fields = [
        HiddenField(u'form_token', modifiers=[FormTokenValidator()]),
        TextArea(u'profile', u'Profile',
                 modifiers=[HtmlModifier()]),
        TextArea(u'premailmessage', u'Pre-mail message',
                 u'A short plain-text message which will be shown '
                 u'before anyone sends you mail.',
                 rows=5,
                 modifiers=[
                     LengthValidator(max_len=User.pre_mail_message_max_length),
                     BlankToNoneModifier()]),
        SubmitButton(title=u'Update', id_=u'submit')
    ]

def edit_profile(req):
    req.check_permission(u'edit_profile')
    defaults = {
        u'form_token': req.form_token(),
        u'profile': (req.user.profile, req.user.rendered_profile),
        u'premailmessage': req.user.pre_mail_message
    }
    form = EditProfileForm(req, defaults)
    context = {'form': form.generate()}
    if form.was_filled and not form.errors:
        values = form.values_dict()
        req.user.profile, req.user.rendered_profile = values[u'profile']
        req.user.pre_mail_message = values[u'premailmessage']
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

def permissions_from_values(values):
    for key, value in values.iteritems():
        if key.startswith(u'perm'):
            try:
                perm_id = int(key[4:])
            except ValueError:
                continue
            if value:
                yield Permission.query.get(perm_id)
    
def subaccount_list(req):
    req.check_permission(None)
    if req.subaccount is not None:
        raise Error403()
    subaccounts = req.user.subaccounts.order_by(Subaccount.name).all()
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
        raise Error403()
        
    class CreateSubaccountForm(Form):
        method = u'post'
        action = 'settings.create_subaccount'
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
        subaccount = Subaccount(req.user, values[u'name'], values[u'password'])
        Session.save(subaccount)
        for permission in permissions_from_values(values):
            subaccount.permissions.append(permission)
        req.redirect('settings.subaccount_list', created=1)
    else:
        return req.render_template('create_subaccount.html',
            form=form.generate())
        
def edit_subaccount(req, subaccount_id):
    req.check_permission(None)
    if req.subaccount is not None:
        raise Error403()
    subaccount = Subaccount.query.get(subaccount_id)
    if subaccount is None:
        return None
        
    class EditSubaccountForm(Form):
        method = u'post'
        action = 'settings.edit_subaccount', dict(subaccount_id=subaccount_id)
        reliable_field = u'form_token'
        fields = [
            HiddenField(u'form_token', modifiers=[FormTokenValidator()])
        ]
        fields += subaccount_permission_fields(req.user)
        fields.append(SubmitButton(title=u'Submit', id_=u'submit'))
    
    defaults = {u'form_token': req.form_token()}
    for permission in subaccount.permissions:
        defaults[u'perm%s' % permission.permission_id] = True
        
    form = EditSubaccountForm(req, defaults)
    if form.was_filled and not form.errors:
        values = form.values_dict()
        current_perms = set(subaccount.permissions)
        selected_perms = set(permissions_from_values(values))
        deleted_perms = current_perms - selected_perms
        added_perms = selected_perms - current_perms
        for deleted_perm in deleted_perms:
            subaccount.permissions.remove(deleted_perm)
        for added_perm in added_perms:
            subaccount.permissions.append(added_perm)
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
        raise Error403()
    subaccount = Subaccount.query.get(subaccount_id)
    if subaccount is None:
        return None
        
    form = SubaccountDeleteForm(req, {u'form_token': req.form_token()})
    form.action = 'settings.delete_subaccount', dict(subaccount_id=subaccount_id)
    if form.was_filled and not form.errors:
        Session.delete(subaccount)
        req.redirect('settings.subaccount_list', deleted=1)
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
        raise Error403
        
    subaccount = Subaccount.query.get(subaccount_id)
    if subaccount is None:
        return None
    
    defaults = {
        u'form_token': req.form_token()
    }
        
    form = SubaccountPasswordChangeForm(req, defaults)
    form.action = 'settings.change_subaccount_password', dict(subaccount_id=subaccount.subaccount_id)
    
    if form.was_filled and not form.errors:
        values = form.values_dict()
        subaccount.change_password(values[u'new_password'])
        req.redirect('settings.subaccount_list', password_changed=1)
    else:
        context = {
            'form': form.generate(),
            'name': subaccount.name
        }
        return req.render_template('change_subaccount_password.html', context)
