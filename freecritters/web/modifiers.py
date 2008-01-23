# -*- coding: utf-8 -*-

"""Form modifiers which are direcrtly related to freeCritters."""

from datetime import datetime, timedelta
from freecritters.web.form import HiddenField, Modifier, ValidationError
from freecritters.model import User, Subaccount, FormToken, Pet, Appearance, Group
from freecritters.textformats import render_html
from HTMLParser import HTMLParseError

class UsernameNotTakenValidator(Modifier):
    """Validates that a username isn't taken."""
    
    def __init__(self, message=u'That username is taken.'):
        self.message = message
    
    def modify(self, value, form):
        if User.find_user(value) is not None:
            raise ValidationError(self.message)
        return value
        
class PetNameNotTakenValidator(Modifier):
    """Validates that a pet name isn't taken."""

    def __init__(self, message=u'That name is taken.'):
        self.message = message

    def modify(self, value, form):
        if Pet.find_pet(value) is not None:
            raise ValidationError(self.message)
        return value

class UserModifier(Modifier):
    """Turns a username into a User object."""
    
    def __init__(self, message=u"That user doesn't exist."):
        self.message = message
    
    def modify(self, value, form):
        user = User.find_user(value)
        if user is None:
            raise ValidationError(self.message)
        return user
    
    def unmodify(self, value, form):
        return value.username

class AppearanceModifier(Modifier):
    """Turns an appearance ID into an appearance object."""
    def __init__(self, message=u"That appearance doesn't exist."):
        self.message = message
    
    def modify(self, value, form):
        try:
            value = int(value)
        except ValueError:
            raise ValidationError(self.message)
        appearance = Appearance.query.get(value)
        if appearance is None:
            raise ValidationError(self.message)
        return appearance
    
    def unmodify(self, value, form):
        return unicode(value.appearance_id)

class SubaccountModifier(Modifier):
    """Turns a subaccount name into a Subaccount object."""
    
    def __init__(self, user_field, message=u"That subaccount doesn't exist."):
        self.user_field = user_field
        self.message = message
    
    def modify(self, value, form):
        if value == u'':
            return None
        else:
            user = form[self.user_field]
            subaccount = Subaccount.query.filter_by(user_id=user.user_id, name=value).first()
            if subaccount is None:
                raise ValidationError(self.message)
            return subaccount
    
    def dependencies(self, form):
        return set((form.field(self.user_field),))

class SubaccountNameNotTakenValidator(Modifier):
    """Validates that a subaccount name doesn't already exist."""
    
    def __init__(self, message=u'Subaccount name taken.'):
        self.message = message
        
    def modify(self, value, form):
        user = form.req.user
        if user.subaccounts.filter_by(name=value)[:1].count():
            raise ValidationError(self.message)
        return value
        
class PasswordValidator(Modifier):
    """Validates that a password is correct."""
    
    def __init__(self, user_field, subaccount_field,
                 message=u'Incorrect password.'):
        self.user_field = user_field
        self.subaccount_field = subaccount_field
        self.message = message
    
    def modify(self, value, form):
        user = form[self.user_field]
        subaccount = form[self.subaccount_field]
        if subaccount is not None:
            password_checker = subaccount
        else:
            password_checker = user
        if not password_checker.check_password(value):
            raise ValidationError(self.message)
        return value
        
    def dependencies(self, form):
        return set((form.field(self.user_field),
                    form.field(self.subaccount_field)))

class CurrentPasswordValidator(Modifier):
    def __init__(self, message=u'Incorrect password.'):
        self.message = message
    
    def modify(self, value, form):
        user = form.req.user
        if not user.check_password(value):
            raise ValidationError(self.message)
                    
class FormTokenValidator(Modifier):
    def __init__(self, message=u"It looks you may not have meant to perform "
                               u"this action. This could be an attempt to "
                               u"scam you. If this submission is not in "
                               u"error, please resubmit the form."):
        self.message = message
    
    def modify(self, value, form):
        form_token = FormToken.find_form_token(value, form.req.user, form.req.subaccount)
        if form_token is None:
            raise ValidationError(self.message)
        return value

class FormTokenField(HiddenField):
    type_name = 'HiddenField'
    def __init__(self, name=u'form_token', id_=None):
        super(FormTokenField, self).__init__(name, id_=id_, modifiers=[FormTokenValidator()])
        
    def default_value(self, form):
        return form.req.form_token()
      
class HtmlModifier(Modifier):    
    def modify(self, value, form):
        try:
            rendered_value = render_html(value)
        except HTMLParseError, e:
            try:
                message = u"There's something wrong with your HTML on line %s." % e.lineno
            except AttributeError:
                message = u"There's something wrong with your HTML."
            raise ValidationError(message)
        return value, rendered_value
        
    def unmodify(self, value, form):
        return value[0]
        
class NotMeValidator(Modifier):
    def __init__(self, message=u'Must not be you.'):
        self.message = message
        
    def modify(self, value, form):
        if form.req.user == value:
            raise ValidationError(self.message)
        return value

class GroupNameNotTakenValidator(Modifier):
    """Validates that a group name isn't taken."""

    def __init__(self, message=u'That name is taken.'):
        self.message = message

    def modify(self, value, form):
        if Group.find_group(value) is not None:
            raise ValidationError(self.message)
        return value

class GroupTypeCompatibilityValidator(Modifier):
    """Validates that a group type is compatible with the user's current
    groups.
    """
    def __init__(self, message=u"That group type is incompatible with a group you've already joined."):
        self.message = message
    
    def modify(self, value, form):
        if not Group.types_can_coexist(int(value), form.req.user.max_group_type):
            raise ValidationError(self.message)
        return value