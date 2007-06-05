# -*- coding: utf-8 -*-

"""Form modifiers which are direcrtly related to freeCritters."""

from datetime import datetime, timedelta
from freecritters.web.form import Modifier, ValidationError
from freecritters.model import User, Subaccount, FormToken
from freecritters.textformats import render_html
from sqlalchemy import Query

class UsernameNotTakenValidator(Modifier):
    """Validates that a username isn't taken."""
    
    def __init__(self, message=u'That username is taken.'):
        self.message = message
    
    def modify(self, value, form):
        if User.find_user(value) is not None:
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

class SubaccountModifier(Modifier):
    """Turns a subaccount name into a Subaccount object."""
    
    def __init__(self, user_field, message=u"That subaccount doesn't exist."):
        self.user_field = user_field
        self.message = message
    
    def modify(self, value, form):
        if value == u'':
            return None
        else:
            user = form.modified_values[self.user_field]
            query = Query(Subaccount)
            subaccount = query.get_by(user_id=user.user_id, name=value)
            if subaccount is None:
                raise ValidationError(self.message)
            return subaccount
    
    def dependencies(self, form):
        return set((form.fields_by_id[self.user_field], ))

class SubaccountNameNotTakenValidator(Modifier):
    """Validates that a subaccount name doesn't already exist."""
    
    def __init__(self, message=u'Subaccount name taken.'):
        self.message = message
        
    def modify(self, value, form):
        user = form.req.user
        for subaccount in user.subaccounts:
            if subaccount.name == value:
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
        user = form.modified_values[self.user_field]
        subaccount = form.modified_values[self.subaccount_field]
        if subaccount is not None:
            password_checker = subaccount
        else:
            password_checker = user
        if not password_checker.check_password(value):
            raise ValidationError(self.message)
        return value
        
    def dependencies(self, form):
        return set((form.fields_by_id[self.user_field],
                    form.fields_by_id[self.subaccount_field]))

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
            
class HtmlModifier(Modifier):
    def __init__(self, message=u"Couldn't parse your text: %s"):
        self.message = message
    
    def modify(self, value, form):
        try:
            rendered_value = render_html(value)
        except ValueError, e:
            raise ValidationError(self.message % e.message)
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
