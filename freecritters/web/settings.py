# -*- coding: utf-8 -*-

from freecritters.web import templates
from freecritters.web.form import Form, HiddenField, TextArea, SelectMenu, \
                                  SubmitButton, LengthValidator
from freecritters.web.modifiers import FormTokenValidator, HtmlModifier
from freecritters.model import User
from colubrid.exceptions import AccessDenied

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
        u'form_token': req.login.form_token(),
        u'profile': (req.login.user.profile, req.login.user.rendered_profile)
    }
    if req.login.user.pre_mail_message is not None:
        defaults['premailmessage'] = req.login.user.pre_mail_message
    form = EditProfileForm(req, defaults)
    context = {u'form': form.generate()}
    if form.was_filled and not form.errors:
        values = form.values_dict()
        req.login.user.profile = values[u'profile'][0]
        req.login.user.rendered_profile = values[u'profile'][1]
        if values['premailmessage'].isspace() or not values['premailmessage']:
            req.login.user.pre_mail_message = None
        else:
            req.login.user.pre_mail_message = values['premailmessage']
        context[u'updated'] = True
    return templates.factory.render('edit_profile', req, context)

def make_subaccount_form_class(user):
    class SubaccountForm(Form):
        method = u'post'
        fields = [
            HiddenField(u'form_token', modifiers=[FormTokenValidator()]),
        ]
        for permission in user.role.permissions:
            fields.append(CheckboxField(
                unicode(permission.permission_id),
                permission.name,
                permission.description
            ))
        fields.append(SubmitButton(title=u'Submit'))
    return SubaccountForm
    
def subaccount_list(req):
    req.check_permission(None)
    if req.login.subaccount is not None:
        raise AccessDenied()
    subaccounts = []
    for subaccount in req.login.user.subaccounts:
        subaccounts.append({
            u'id': subaccount.subaccount_id,
            u'name': subaccount.name
        })
    context = {
        u'subaccounts': subaccounts
    }
    return templates.factory.render('subaccount_list', req, context)
