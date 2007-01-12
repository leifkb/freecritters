# -*- coding: utf-8 -*-

"""Relatively simple library for form validation. Made for Colubrid and Jinja.

This is designed similarly to Pocoo's pocoo.utila.forms, but with fewer
features and without a dependency on Pocoo.
"""

class ValidationError(Exception):
    """Raised by Modifiers when a value fails validation. Should contain a
    unicode string describing the error.
    """

class FieldNotFilled(Exception):
    """Raised by form fields when they aren't present."""
    
class Modifier(object):
    """Modifiers modify and/or validate form values after they're provided
    by the user. They can be chained together to e.g. validate an integer
    value (for range, etc.) which has been converted from a string.
    """
    
    def __init__(self):
        pass
    
    def modify(self, value, form):
        """Takes a value and returns another one. Raises ValidationError if
        there was an error.
        """
        
        return value
    
    def unmodify(self, value, form):
        """Takes a modified value and returns it in unmodified form. This is
        roughly the opposite of modify.
        """
        
        return value
    
class IntegerModifier(Modifier):
    """Turns a string value into an integer, or causes an error if it's not
    valid.
    """
    
    def __init__(self, message=u'Must be an integer.', base=10):
        super(IntegerModifier, self).__init__()
        self.message = message
        self.base = base
    
    def modify(self, value, form):
        try:
            return int(value, self.base)
        except ValueError:
            raise ValidationError(self.message)
    
    def unmodify(self, value, form):
        return unicode(value)
            
class RangeValidator(Modifier):
    def __init__(self, min_val=None, max_val=None, message=None):
        super(RangeValidator, self).__init__()
        self.min_val = min_val
        self.max_val = max_val
        if message is None:
            if min_val is not None and max_val is not None:
                message = u'Must be between %s and %s (inclusive).' \
                                                 % (min_val, max_val)
            elif min_val is not None:
                message = u'Must be at least %s.' % min_val
            elif max_val is not None:
                message = u'Must be at most %s.' % max_val
            else:
                message = u'The universe is exploding! Drop your computer and run!'
        self.message = message
    
    def modify(self, value, form):
        if (self.min_val is not None and value < self.min_val) \
        or (self.max_val is not None and value > self.max_val):
            raise ValidationError(self.message)
        return value

class LengthValidator(Modifier):
    def __init__(self, min_len=None, max_len=None, message=None):
        super(LengthValidator, self).__init__()
        self.min_len = min_len
        self.max_len = maxlen
        if message is None:
            if min_len is not None and max_len is not None:
                message = u'Must be %s-%s (inclusive) characters.' \
                                                % (min_len, max_len)
            elif max_len is not None:
                message = u'Must be at most %s characters long' % max_len
            elif min_len is not None:
                message = u'Most be at least %s characters long.' % min_len
            else:
                message = u'The aliens are coming! THE ALIENS ARE COMING!'
        self.message = message
        
    def modify(self, value, form):
        if (self.min_len is not None and len(value) < self.min_len) \
        or (self.max_len is not None and len(value) > self.max_val):
            raise ValidationError(self.message)
        return value

class SameAsValidator(Modifier):
    """Validates that one field's value is the same as another."""
    
    def __init__(self, other_field_id, message=None):
        self.other_field_id = other_field_id
        self.message = message
    
    def modify(self, value, form):
        if value != form.values[self.other_field_id]:
            message = self.message
            if message is None:
                message = u"Must be the same as '%s'." \
                                % form.fields_by_id[self.other_field_id].title
                raise ValidationError(message)
        return value

class RegexValidator(Modifier):
    """Validates that a text field matches a regex."""
    
    def __init__(self, regex, message=u'Must be properly formatted.'):
        if isinstance(regex, basestring):
            regex = re.compile(regex)
        self.regex = regex
    
    def modify(self, value, form):
        if self.regex.search(value) is None:
            raise ValidationError(self.message)
        
class FormField(object):
    """Base class for form fields."""
    
    def __init__(self, name, title, description=u'', id_=None, modifiers=None,
                 must_be_present=True):
        if modifiers is None:
            modifiers = []
        if id_ is None:
            assert name is not None, u'Name and id must not both be None.'
            id_ = name
        self.id_ = id_
        self.title = title
        self.description = description
        self.name = name
        self.modifiers = modifiers
        self.must_be_present = must_be_present
        
    def value_from_raw(self, values):
        """Takes a list (like what req.form.getlist(name) would return) of
        values in the request with the same name as this field and returns the
        field's value. If there is no value, raises FieldNotFilled.
        """
        
        try:
            return values[0]
        except IndexError:
            raise FieldNotFilled()

    def modify_value(self, value, form):
        """Runs a value through the field's modifiers and returns it or
        raises ValidationError.
        """
        
        for modifier in self.modifiers:
            value = modifier.modify(value, form)
        return value
    
    def unmodify_value(self, value, form):
        """Runs a modified value through the field's modifiers in reverse and
        returns an unmodified value.
        """
        
        for modifier in reversed(self.modifiers):
            value = modifier.unmodify(value, form)
        return value
    
    def template_context(self, form):
        """Returns a dictionary which contains all information that a
        template will need about this field.
        """
        
        result = dict(
            type=type(self).__name__,
            title=self.title,
            name=self.name,
            description=self.description,
            id=self.id_,
            error=form.errors.get(self.id_),
            has_value=False
        )
        if self.id_ in form.values:
            result['has_value'] = True
            result['value'] = form.values[self.id_]
        return result

class TextField(FormField):
    """Text fields (<input type="text">)."""
    
    def __init__(self, name, title, description=u'', max_length=None,
                 size=None, id_=None, modifiers=None, must_be_present=True):
        if modifiers is None:
            modifiers = []
        if max_length is not None:
            modifiers.insert(0, LengthValidator(None, max_length))
        super(TextField, self).__init__(name, title, description, id_,
                                        modifiers, must_be_present)
        self.max_length = max_length
        self.size = size
    
    def template_context(self, form):
        result = super(TextField, self).template_context(form)
        result['size'] = self.size
        result['max_length'] = self.max_length
        return result

class PasswordField(TextField):
    """Password fields (<input type="password")."""
        
class CheckBox(FormField):
    """Check boxes (<input type="checkbox")."""
    
    def __init__(self, name, title, description=u'', value=u'-', id_=None, 
                 modifiers=None, must_be_present=True):
        super(CheckBox, self).__init__(name, title, description, id_,
                                       modifiers, must_be_present)
        self.value = value
    
    def value_from_raw(self, values):
        return self.value in values
    
    def template_context(self, form):
        result = super(CheckBox, self).template_context(form)
        result['raw_value'] = self.value # Terrible name!
        return result
        
class TextArea(FormField):
    """Text areas (<textarea></textarea>)."""
    
    def __init__(self, name, title, description=u'', rows=12, cols=50,
                 id_=None, modifiers=None, must_be_present=True):
        super(TextArea, self).__init__(name, title, description, id_,
                                       modifiers, must_be_present)
        self.rows = rows
        self.cols = cols
    
    def template_context(self, form):
        result = super(TextArea, self).template_context(form)
        result['rows'] = self.rows
        result['cols'] = self.cols

class SelectMenu(FormField):
    """Select menus (<select>...</select>)."""
    
    def __init__(self, name, title, description=u'', options=None, id_=None,
                 modifiers=None, must_be_present=True):
        super(SelectMenu, self).__init__(name, title, description, id_,
                                         modifiers, must_be_present)
        self.options = options
    
    def value_from_raw(self, values):
        value = super(SelectMenu, self).value_from_raw(values)
        for option_value, option_caption in self.options:
            if option_value == value:
                return value
        else:
            # If the user gives a non-existant value, we silently act like
            # the field wasn't filled in at all. Is this the right solution?
            raise FieldNotFilled()
    
    def template_context(self, form):
        result = super(SelectMenu, self).template_context(form)
        options = []
        for value, caption in self.options:
            options.append({'value': value, 'caption': caption})
        result['options'] = options
        return result

class HiddenField(FormField):
    """Hidden fields (<input type="hidden">)."""
    
class SubmitButton(FormField):
    """Submit buttons (<input type="submit">). Note that name can be None,
    but id must be specified explicitly in that case.
    
    Title is used as the button's value. (Blame IE's for that.)
    """
    
    def __init__(self, name=None, title=u'', description=u'', id_=None,
                 modifiers=None, must_be_present=False):
        super(SubmitButton, self).__init__(name, title, description, id_,
                                           modifiers, must_be_present)
    
class FormMeta(type):
    def __init__(cls, name, bases, dict_):
        # Form isn't in the namespace when it's being created,
        # so we can't use 'and'.
        if bases != (object,):
            assert bases == (Form,), u'Forms can inherit only from Form.'
        assert cls.method in (u'get', u'post'), \
            u'Form method must be get or post.'
        cls.fields_by_id = {}
        for field in dict_['fields']:
            if field.id_ in cls.fields_by_id:
                raise ValueError(u'Duplicate id %s.' % field.id_)
            cls.fields_by_id[field.id_] = field
            
class Form(object):
    """Forms. Subclasses represent individual forms; instances represent
    loads of those forms. Create a form like this:
    
    class FooForm(Form):
        method = u'post'
        action = u'/path/to/me'
        fields = [
            TextField(u'name', u'Name'),
            TextField(u'age', u'Age', modifiers=[IntegerModifier(),
                                                 RangeValidator(1, 130)]),
            SubmitButton(title=u'Submit', id_=u'submit')
        ]
    
    And use it like this:
        
    foo = FooForm(req.form, defaults)
    if foo.was_filled and not foo.errors:
        values = foo.values_dict()
        # Do something with values
    else:
        template_data = foo.generate()
        # Fill a template with template_data
    """
    
    __metaclass__ = FormMeta
    
    method = u'post'
    action = u''
    fields = []
    
    def __init__(self, req, defaults=None, data=None):
        """Initializes an instance (load) of the form. req is the Colubrid
        Request; defaults is a mapping keyed on field id which contains
        default field values. data is a MultiDict of data; if it's not
        present, it's pulled from req (req.form if method is post, req.args
        if method is get).
        """
        
        if defaults is None:
            defaults = {}
        if data is None:
            if self.method == u'get':
                data = req.args
            else:
                data = req.form
        self.defaults = defaults
        self.values = {}
        self.modified_values = {}
        self.errors = {}
        self.was_filled = True
        fields_to_modify = []
        for field in self.fields:
            has_value = False
            try:
                value = field.value_from_raw(data.getlist(field.name))
                self.values[field.id_] = value
                fields_to_modify.append(field)
            except FieldNotFilled:
                if field.must_be_present:
                    self.was_filled = False
                try:
                    modified_value = defaults[field.id_]
                    value = field.unmodify_value(modified_value, self)
                    self.values[field.id_] = value
                    self.modified_values[field.id_] = modified_value
                except KeyError:
                    pass
            except ValidationError, e:
                self.errors[field.id_] = e.message
        for field in fields_to_modify:
            value = self.values[field.id_]
            try:
                modified_value = field.modify_value(value, self)
            except ValidationError, e:
                self.errors[field.id_] = e.message
            self.modified_values[field.id_] = modified_value
            
    def values_dict(self):
        """Returns the values of fields in the form which have values (either
        default or user-provided) as a dict, keyed by field id. This dict can
        be safely mutated.
        """
        
        return self.modified_values.copy()
    
    def generate(self):
        """Generates a dictionary of data about the form, suitable for use in
        a Jinja template.
        """
        
        result = {}
        result['method'] = self.method
        result['action'] = self.action
        result['fields'] = []
        result['fields_dict'] = {}
        result['has_errors'] = bool(self.errors)
        for field in self.fields:
            field_data = field.template_context(self)
            result['fields'].append(field_data)
            result['fields_dict'][field.id_] = field_data
        return result
