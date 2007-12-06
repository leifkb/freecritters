# -*- coding: utf-8 -*-

"""Relatively simple library for form validation. Works with Werkzeug.

This is designed similarly to Pocoo's pocoo.utils.forms, but with fewer
features and without a dependency on Pocoo.
"""

import ImageColor

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
    
    def dependencies(self, form):
        """Returns a set of fields that fields modified by this modifier
        depend on. Dependencies must be modified before their dependents.
        """
        
        return set()
    
class IntegerModifier(Modifier):
    """Turns a string value into an integer, or causes an error if it's not
    valid.
    """
    
    def __init__(self, message=u'Must be a number.', base=10):
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
        self.max_len = max_len
        if message is None:
            if min_len is not None and max_len is not None:
                message = u'Must be %s-%s (inclusive) characters.' \
                                                % (min_len, max_len)
            elif max_len is not None:
                message = u'Must be at most %s characters long' % max_len
            elif min_len is not None:
                message = u'Must be at least %s characters long.' % min_len
            else:
                message = u'The aliens are coming! THE ALIENS ARE COMING!'
        self.message = message
        
    def modify(self, value, form):
        if (self.min_len is not None and len(value) < self.min_len) \
        or (self.max_len is not None and len(value) > self.max_len):
            raise ValidationError(self.message)
        return value

class SameAsValidator(Modifier):
    """Validates that one field's value is the same as another."""
    
    def __init__(self, other_field_id, message=None):
        self.other_field_id = other_field_id
        self.message = message
    
    def modify(self, value, form):
        if value != form.field_results(self.other_field_id).value:
            message = self.message
            if message is None:
                message = u'Must be the same as "%s".' \
                                % form.field_results(self.other_field_id).field.title
                raise ValidationError(message)
        return value

class RegexValidator(Modifier):
    """Validates that a text field matches a regex."""
    
    def __init__(self, regex, message=u'Must be properly formatted.'):
        if isinstance(regex, basestring):
            regex = re.compile(regex)
        self.regex = regex
        self.message = message
    
    def modify(self, value, form):
        if self.regex.search(value) is None:
            raise ValidationError(self.message)
        return value

class BlankToNoneModifier(Modifier):
    """Transforms a blank (empty or all-spaces) string into None."""
    
    def modify(self, value, form):
        if not value or value.isspace():
            return None
        else:
            return value
    
    def unmodify(self, value, form):
        if value is None:
            return u''
        else:
            return value

class ColorModifier(Modifier):
    """Modifies a color name or hex string into an (r, g, b) tuple, where
    all values are in the range 0-255.
    """
    
    def __init__(self, message=u'Not a valid color.'):
        self.message = message
    
    def modify(self, value, form):
        try:
            return ImageColor.getrgb(value)
        except ValueError:
            raise ValidationError(self.message)
    
    def unmodify(self, value, form):
        return u'#%02X%02X%02X' % value
        
class FormField(object):
    """Base class for form fields."""
    
    def __init__(self, name, title=u'', description=u'', id_=None,
                 modifiers=None, must_be_present=True):
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
        self.keep_failed_values = True
        
    def value_from_raw(self, values, form):
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
    
    def dependencies(self, form):
        """Returns a set of fields that this field depends on."""
        
        result = set()
        for modifier in self.modifiers:
            result.update(modifier.dependencies(form))
        return result
    
    def default_value(self, form):
        """Returns a default value for the field. This is overridden by
        the default specified when the Form is called.
        
        Raises FieldNotFilled to indicate that there is no default
        available.
        """
        
        raise FieldNotFilled()
    
    @property
    def type_name(self):
        return type(self).__name__
    
class TextField(FormField):
    """Text fields (<input type="text">)."""
    
    def __init__(self, name, title=u'', description=u'', max_length=None,
                 size=None, id_=None, modifiers=None, must_be_present=True):
        if modifiers is None:
            modifiers = []
        if max_length is not None:
            modifiers.insert(0, LengthValidator(None, max_length))
        super(TextField, self).__init__(name, title, description, id_,
                                        modifiers, must_be_present)
        self.max_length = max_length
        self.size = size
        
class ColorSelector(TextField):
    """Field for picking a color."""
    
    def __init__(self, name, title, description=u'', size=None, id_=None,
                 modifiers=None, must_be_present=True):
        if modifiers is None:
            modifiers = []
        modifiers.insert(0, ColorModifier())
        super(ColorSelector, self).__init__(
            name, title, description, None, size, id_, modifiers, must_be_present
        )

class PasswordField(TextField):
    """Password fields (<input type="password">)."""
        
class CheckBox(FormField):
    """Check boxes (<input type="checkbox">)."""
    
    def __init__(self, name, title=u'', description=u'', value=u'-', id_=None, 
                 modifiers=None, must_be_present=True):
        super(CheckBox, self).__init__(name, title, description, id_,
                                       modifiers, must_be_present)
        self.value = value
    
    def value_from_raw(self, values, results):
        if not results.reliable_field_filled:
            raise FieldNotFilled()

        return self.value in values
        
class TextArea(FormField):
    """Text areas (<textarea></textarea>)."""
    
    def __init__(self, name, title=u'', description=u'', rows=12, cols=42,
                 id_=None, modifiers=None, must_be_present=True):
        super(TextArea, self).__init__(name, title, description, id_,
                                       modifiers, must_be_present)
        self.rows = rows
        self.cols = cols

class SelectMenu(FormField):
    """Select menus (<select>...</select>)."""
    
    def __init__(self, name, title=u'', description=u'', options=None,
                 id_=None, modifiers=None, must_be_present=True):
        super(SelectMenu, self).__init__(name, title, description, id_,
                                         modifiers, must_be_present)
        self.options = options
    
    def value_from_raw(self, values, form):
        value = super(SelectMenu, self).value_from_raw(values, form)
        for option_value, option_caption in self.options:
            if option_value == value:
                return value
        else:
            # If the user gives a non-existent value, we silently act like
            # the field wasn't filled in at all. Is this the right solution?
            raise FieldNotFilled()

class HiddenField(FormField):
    """Hidden fields (<input type="hidden">)."""
    
    def __init__(self, name, title=u'', description=u'', id_=None,
                 modifiers=None, must_be_present=True):
        super(HiddenField, self).__init__(name, title, description, id_,
                                          modifiers, must_be_present)
        self.keep_failed_values = False
    
class SubmitButton(FormField):
    """Submit buttons (<input type="submit">). Note that name can be None,
    but id must be specified explicitly in that case.
    
    Title is used as the button's value. (Blame IE for that.)
    """
    
    def __init__(self, name=None, title=u'', description=u'', id_=None,
                 modifiers=None, must_be_present=False):
        super(SubmitButton, self).__init__(name, title, description, id_,
                                           modifiers, must_be_present)
                                           
class Form(object):
    def __init__(self, method, action, *fields, **kws):
        self.method = method
        self.action = action
        self._fields = []
        self._fields_by_id = {}
        self.id_prefix = kws.pop('id_prefix', u'')
        self.reliable_field = kws.pop('reliable_field', None)
        self._dependency_ordered_fields = None
        if kws:
            raise ArgumentError("Unknown keyword argument(s): %r" % kws.keys())
        for field in fields:
            self.add_field(field)
    
    def add_field(self, field):
        if field.id_ in self._fields_by_id:
            raise ValueError("Duplicate ID: %r" % field.id_)
        self._dependency_ordered_fields = None
        self._fields_by_id[field.id_] = field
        self._fields.append(field)
    
    def __iter__(self):
        return iter(self._fields)
    
    def field(self, field_or_id):
        if not isinstance(field_or_id, basestring):
            field_or_id = field_or_id.id_
        return self._fields_by_id[field_or_id] 
    
    def _generate_dependency_ordered_fields(self):
        fields = list(self)
        if self.reliable_field is not None:
            reliable_field = self.field(self.reliable_field)
            assert not reliable_field.dependencies(self), \
                'Reliable field must not have dependencies,'
            reliable_field_index = fields.index(reliable_field)
            fields[reliable_field_index] = fields[0]
            fields[0] = reliable_field
        # This algorithm is disgustingly inefficient. But it's used rarely,
        # and on small data sets, so I'm not going to bother to optimize it.
        # I'm a bad person.
        while True:
            encountered = set()
            for field_index, field in enumerate(fields):
                encountered.add(field)
                unmet_dependencies = field.dependencies(self) - encountered
                if unmet_dependencies:
                    max_index = 0
                    for dependency in unmet_dependencies:
                        dependency = self.field(dependency)
                        index = fields.index(dependency)
                        if index > max_index:
                            max_index = index
                    fields[field_index] = fields[max_index]
                    fields[max_index] = field
                    break
            else:
                break
        self._dependency_ordered_fields = fields
    
    @property
    def dependency_ordered_fields(self):
        if self._dependency_ordered_fields is None:
            self._generate_dependency_ordered_fields()
        return iter(self._dependency_ordered_fields)
    
    def __call__(self, req, form_defaults=None):
        if form_defaults is None:
            form_defaults = {}
        
        return FormResults(req, self, form_defaults)
        
class FieldResults(object):
    def __init__(self, form_results, field, filled, has_value, value,
                 has_modified_value, modified_value, error):
        self.form_results = form_results
        self.field = field
        self.filled = filled
        self.has_value = has_value
        if has_value:
            self.value = value
        self.has_modified_value = has_modified_value
        if has_modified_value:
            self.modified_value = modified_value
        self.error = error

class FormResults(object):
    def __init__(self, req, form, form_defaults):
        self.req = req
        self.form = form
        self.action = form.action
        self.has_errors = False
        self.filled = True
        self._field_results = []
        self._field_results_by_id = {}
        
        defaults = {}
        for field in form:
            try:
                defaults[field.id_] = field.default_value(self)
            except FieldNotFilled:
                pass
        defaults.update(form_defaults)
        
        if form.method == u'get':
            data = req.args
        else:
            data = req.form
            
        for field in form.dependency_ordered_fields:
            error = None
            value = None
            has_value = False
            modified_value = None
            has_modified_value = False
            filled = False
            try:
                value = field.value_from_raw(data.getlist(field.name), self)
            except FieldNotFilled:
                if field.must_be_present:
                    self.filled = False
                try:
                    modified_value = defaults[field.id_]
                except KeyError:
                    pass
                else:
                    has_modified_value = True
                    value = field.unmodify_value(modified_value, self)
                    has_value = True
            else:
                has_value = True
                filled = True
                for dependency in field.dependencies(self.form):
                    if not self.field_results(dependency).has_modified_value:
                        break
                else:
                    try:
                        modified_value = field.modify_value(value, self)
                    except ValidationError, e:
                        error = e.message
                        self.has_errors = True
                        if not field.keep_failed_values:
                            try:
                                value = field.unmodify_value(defaults[field.id_], self)
                            except KeyError:
                                pass
                    else:
                        has_modified_value = True
            results = FieldResults(self, field, filled, has_value, value,
                                   has_modified_value, modified_value, error)
            self._field_results.append(results)
            self._field_results_by_id[field.id_] = results
    
    @property
    def successful(self):
        return self.filled and not self.has_errors
    
    @property
    def reliable_field_filled(self):
        reliable_field = self.form.reliable_field
        if reliable_field is None:
            raise ValueError('Reliable field required.')
        return self.field_results(reliable_field).filled
    
    @property
    def action_url(self):
        if isinstance(self.action, basestring):
            return self.req.url_for(self.action)
        else:
            return self.req.url_for(self.action[0], **self.action[1])
    
    def __iter__(self):
        return iter(field_results.field.id_ for field_results in self._field_results if field_results.has_modified_value)
    
    def iterkeys(self):
        return iter(self)
    
    def keys(self):
        return list(self)
    
    def __contains__(self, field_or_id):
        try:
            field_results = self.field_results(field_or_id)
        except KeyError:
            return False
        return field_results.has_modified_value
    
    def __getitem__(self, field_or_id):
        field_results = self.field_results(field_or_id)
        if not field_results.has_modified_value:
            raise KeyError(field_or_id)
        return field_results.modified_value
    
    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default
    
    def field_results(self, field_or_id):
        if not isinstance(field_or_id, basestring):
            field_or_id = field_or_id.id_
        return self._field_results_by_id[field_or_id]