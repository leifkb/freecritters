"""Sanitizes HTML using configurable rules."""

from HTMLParser import HTMLParser
from xml.sax.saxutils import escape, quoteattr
from StringIO import StringIO
from itertools import islice
import re

REAL, SYNTHETIC, REMOVED, NEEDS_CONTENT = xrange(4)

class Attribute(object):
    """Represents a type of attribute."""
    
    def __init__(self, required=False, default=None, singular=True):
        self.required = required
        self.default = default
        self.singular = singular
        
    def validate(self, value):
        """Validates that a value is acceptable."""
        
        return True
        
    def modify(self, values):
        """Values is a list of values given for the attribute. Returns a list
        of new values for the attribute, or None if the element is invalid.
        """
        
        if self.singular:
            values = values[:1]
        new_values = []
        for value in values:
            if self.validate(value):
                new_values.append(value)
        if self.required and not new_values:
            if self.default is not None:
                new_values = self.default
            else:
                return None
        return new_values
            

class Element(object):
    """Represents a type of HTML element."""
    
    def __init__(self, attrs=None, can_contain=None, can_create=None,
                 self_closing=False, empty=False, must_have_content=False):
        if attrs is None:
            attrs = {}
        if can_contain is None:
            can_contain = set()
        if can_create is None:
            can_create = []
        self.attrs = attrs
        self.can_contain = can_contain
        self.can_create = can_create
        self.self_closing = self_closing
        self.empty = empty
        self.must_have_content = must_have_content
        
    def start_tag(self, name, attrs):
        attr_text = []
        for attr_name, attr_val in attrs:
            if attr_val is None:
                attr_text.append(u'%s' % (attr_name))
            else:
                attr_text.append(u'%s=%s' % (attr_name, quoteattr(attr_val)))
        if attr_text:
            return u'<%s %s>' % (name, u' '.join(attr_text))
        else:
            return u'<%s>' % name
        
    def end_tag(self, name, attrs):
        return u'</%s>' % name
        
    def process_attrs(self, attrs):
        attr_dict = {}
        for name, value in attrs:
            if name in attr_dict:
                attr_dict[name].append(value)
            elif name in self.attrs:
                attr_dict[name] = [value]
        new_attrs = []
        for attr in self.attrs:
            if attr in attr_dict:
                values = attr_dict[attr]
            else:
                values = []
            values = self.attrs[attr].modify(values)
            if values is None:
                return None
            for value in values:
                new_attrs.append((attr, value))
        return new_attrs
            
class HtmlSanitizer(HTMLParser):
    """Sanitizes HTML. This class is subclassed to define rulesets."""
    
    def __init__(self, profile):
        HTMLParser.__init__(self)
        self.profile = profile
        self.stack = []
        self.result = StringIO(u'')
        self._data = []
        
    def _containers(self):
        index = len(self.stack) - 1
        for item_type, name, attrs in reversed(self.stack):
            if item_type != REMOVED:
                yield index, self.profile.elements[name].can_contain, item_type
            index -= 1
        yield -1, self.profile.root_can_contain, None
        
    def _pop_stack_down_to(self, index):
        cur_index = len(self.stack) - 1
        while cur_index >= index:
            item_type, name, attrs = self.stack.pop()
            if item_type not in (REMOVED, NEEDS_CONTENT):
                self.result.write(
                    self.profile.elements[name].end_tag(name, attrs))
            cur_index -= 1
            
    def _make_containable(self, name):
        if name is None:
            can_create = self.profile.text_can_create
            self_closing = False
        else:
            can_create = self.profile.elements[name].can_create
            self_closing = self.profile.elements[name].self_closing
        containers = self._containers()
        is_first_nonsynth = True
        for stack_index, can_contain, item_type in containers:
            if name in can_contain:
                self._pop_stack_down_to(stack_index + 1)
                return True
            if self_closing and self.stack and \
               len(self.stack) - 1 == stack_index:
                stack_index2 = len(self.stack) - 1
                while stack_index2 >= 0:
                    item_type2, name2, attrs2 = self.stack[stack_index2]
                    if item_type2 not in (REMOVED, SYNTHETIC):
                        if name2 == name:
                            self._pop_stack_down_to(stack_index2)
                            return True
                        break
                    stack_index2 -= 1
                    
            if item_type != SYNTHETIC and is_first_nonsynth:
                for create_name, create_attrs in can_create:
                    if create_name in can_contain:
                        self._pop_stack_down_to(stack_index + 1)
                        self.handle_starttag(create_name, create_attrs, True)
                        return True
                is_first_nonsynth = False
        return False
        
    def _write_top_of_stack(self):
        index = self._containers()[0]
        item_type, name, attrs = self.stack[index]
        self.result.write(self.elements[name].start_tag(attrs))
        
    def _content_encountered(self):
        index = len(self.stack) - 1
        tags_to_write = []
        for item_type, name, attrs in reversed(self.stack):
            if item_type == NEEDS_CONTENT:
                self.stack[index] = (REAL, name, attrs)
                tags_to_write.append(
                    self.profile.elements[name].start_tag(name, attrs))
            elif item_type != REMOVED:
                break
            index -= 1
        for tag in reversed(tags_to_write):
            self.result.write(tag)
        
            
    def handle_starttag(self, name, attrs, synthetic=False):
        self._process_data()
        if name not in self.profile.elements:
            self.stack.append((REMOVED, name, attrs))
            return
        attrs = self.profile.elements[name].process_attrs(attrs)
        if attrs is None: # Invalid attrs
            self.stack.append((REMOVED, name, attrs))
            return
        if not self._make_containable(name):
            if not self.profile.elements[name].empty:
                self.stack.append((REMOVED, name, attrs))
        else:
            if synthetic or not self.profile.elements[name].must_have_content:
                self._content_encountered()
                self.result.write(
                    self.profile.elements[name].start_tag(name, attrs))
            if not self.profile.elements[name].empty:
                if synthetic:
                    item_type = SYNTHETIC
                elif self.profile.elements[name].must_have_content:
                    # Synthetic content-needing elements aren't a concern,
                    # since synthetic items are created along with their
                    # content.
                    # (It took me a few minutes to realize that. I'm dumb.)
                    item_type = NEEDS_CONTENT
                else:
                    item_type = REAL
                self.stack.append((item_type, name, attrs))
    
    def handle_endtag(self, name, synthetic=False):
        self._process_data()
        index = len(self.stack) - 1
        for item_type, item_name, item_attrs in reversed(self.stack):
            if item_name == name and (item_type == SYNTHETIC) == synthetic:
                self._pop_stack_down_to(index)
                return
            index -= 1
    
    _line_break_re = re.compile(u'((?:\r\n|\r|\n)+|[^\r\n]+)')
    
    def handle_data(self, data):
        if not data.isspace():
            self._content_encountered()
        self._data.append(data)
    
    def _process_data(self):
        if not self._data:
            return
        data = u''.join(self._data)
        self._data = []
        if self.profile.line_break_element is None \
           and self.profile.paragraph_element is None:
            if data.isspace() or self._make_containable(None):
                if not data.isspace():
                    # Technically, this is bad since spaces will end up 
                    # outside of presently-empty content-requiring elements.
                    # But it's not a big deal, and it would be a pain to fix.
                    self._content_encountered()
                self.result.write(escape(data))
        else:
            for text in self._line_break_re.findall(data):
                if self.profile.paragraph_element is not None \
                    and text[0] in (u'\r', u'\n') \
                    and text not in (u'\r', u'\n', u'\r\n'):
                    self.handle_endtag(self.profile.paragraph_element, True)
                elif self.profile.line_break_element is not None \
                     and text[0] in (u'\r', u'\n'):
                    self.handle_starttag(self.profile.line_break_element, [],
                                         True)
                else:
                    if text.isspace() or self._make_containable(None):
                        if not text.isspace():
                            self._content_encountered()
                        self.result.write(escape(text))
            
    def close(self):
        HTMLParser.close(self)
        self._process_data()
        self._pop_stack_down_to(0)

class SanitizerProfile(object):
    elements = {}
    root_can_contain = set()
    text_can_create = []
    line_break_element = None
    paragraph_element = None
    
    def __init__(self, elements=None, root_can_contain=None,
                 text_can_create=None, line_break_element=None,
                 paragraph_element=None):
        if elements is not None:
            self.elements = elements
        if root_can_contain is not None:
            self.root_can_contain = root_can_contain
        if text_can_create is not None:
            self.text_can_create = text_can_create
        if line_break_element is not None:
            self.line_break_element = line_break_element
        if paragraph_element is not None:
            self.paragraph_element = paragraph_element
    
_whitespace_re = re.compile(u'\s+')
            
class NoScriptUrlAttribute(Attribute):
    def validate(self, value):
        value = _whitespace_re.sub(u'', value)
        return not (value.startswith(u'javascript:') 
                 or value.startswith(u'vbscript:'))

class ReplacedElement(Element):
    def __init__(self, replace_with, attrs=None, can_contain=None,
                 can_create=None, self_closing=False, empty=False,
                 must_have_content=False):
        super(ReplacedElement, self).__init__(
            attrs, can_contain, can_create, self_closing, empty,
            must_have_content)
        self.replace_with = replace_with
    
    def start_tag(self, name, attrs):
        return super(ReplacedElement, self).start_tag(
            self.replace_with, attrs)
    
    def end_tag(self, name, attrs):
        return super(ReplacedElement, self).end_tag(self.replace_with, attrs)
    
class TestProfile(SanitizerProfile):
    elements = {
        u'p': Element({u'title': Attribute()},
                      set((None, u'br', u'img', u'a', u'em', u'strong', u'i',
                           u'b')),
                      must_have_content=True),
        u'ul': Element({u'title': Attribute()}, set((u'li',)),
                       must_have_content=True),
        u'ol': Element({u'title': Attribute()}, set((u'li',)),
                       must_have_content=True),
        u'li': Element({u'title': Attribute()}, set((u'ol', u'ul', u'p')),
                       [(u'ul', [])], True, must_have_content=True),
        u'br': Element({u'title': Attribute()}, empty=True),
        u'blockquote': Element({u'title': Attribute()},
                               set((u'p', u'ul', u'ol', u'img', u'blockquote',
                                    u'h1', u'h2', u'h3', u'h4', u'h5', u'h6')),
                               must_have_content=True),
        u'img': Element({u'src': NoScriptUrlAttribute(True),
                         u'alt': Attribute(True, [u'']),
                         u'title': Attribute()},
                         [(u'li', [])], empty=True),
        u'a': Element({u'href': Attribute(True), u'title': Attribute()},
                      set((u'strong', u'em', None)),
                      [(u'p', []), (u'li', [])], must_have_content=True),
        u'em': Element({u'title': Attribute()}, set((None, u'strong', u'a')),
                       [(u'p', []), (u'li', [])], must_have_content=True),
        u'strong': Element({u'title': Attribute()}, set((None, u'em', u'a')),
                           [(u'p', []), (u'li', [])], must_have_content=True),
        u'i': ReplacedElement(u'em', {u'title': Attribute()},
                              set((None, u'strong', u'b', u'a')),
                              [(u'p', []), (u'li', [])],
                              must_have_content=True),
        u'b': ReplacedElement(u'strong', {u'title': Attribute()},
                              set((None, u'em', u'i', u'a')),
                              [(u'p', []), (u'li', [])],
                              must_have_content=True),
        u'h1': Element({u'title': Attribute()}, set((None, u'br', u'em', u'a',
                                                     u'strong', u'img')),
                       must_have_content=True),
        u'h2': Element({u'title': Attribute()}, set((None, u'br', u'em', u'a',
                                                     u'strong', u'img')),
                       must_have_content=True),
        u'h3': Element({u'title': Attribute()}, set((None, u'br', u'em', u'a',
                                                     u'strong', u'img')),
                       must_have_content=True),
        u'h4': Element({u'title': Attribute()}, set((None, u'br', u'em', u'a',
                                                     u'strong', u'img')),
                       must_have_content=True),
        u'h5': Element({u'title': Attribute()}, set((None, u'br', u'em', u'a',
                                                     u'strong', u'img')),
                       must_have_content=True),
        u'h6': Element({u'title': Attribute()}, set((None, u'br', u'em', u'a',
                                                     u'strong', u'img')),
                       must_have_content=True),
    }
    root_can_contain = set((u'p', u'ul', u'ol', u'img', u'blockquote',
                            u'h1', u'h2', u'h3', u'h4', u'h5', u'h6'))
    text_can_create = [(u'p', []), (u'li', [])]
    line_break_element = u'br'
    paragraph_element = u'p'
    
class TestProfile2(SanitizerProfile):
    elements = {
        u'p': Element({u'title': Attribute()},
                      set((None, u'br', u'img', u'a', u'em', u'strong')),
                      must_have_content=True),
        u'ul': Element({u'title': Attribute()}, set((u'li',)),
                       must_have_content=True),
        u'ol': Element({u'title': Attribute()}, set((u'li',)),
                       must_have_content=True),
        u'li': Element({u'title': Attribute()},
                       set((None, u'ol', u'ul', u'p', u'blockquote', u'em',
                            u'a', u'strong', u'i', u'b')),
                       [(u'ul', [])], True, must_have_content=True),
        u'br': Element({u'title': Attribute()}, empty=True),
        u'blockquote': Element({u'title': Attribute()},
                               set((None, u'p', u'ul', u'ol', u'img',
                                    u'blockquote',
                                    u'h1', u'h2', u'h3', u'h4', u'h5', u'h6',
                                    u'a', u'em', u'strong', u'br', u'i',
                                    u'b')),
                               must_have_content=True),
        u'img': Element({u'src': NoScriptUrlAttribute(True),
                         u'alt': Attribute(True, [u'']),
                         u'title': Attribute()},
                         [(u'li', [])], empty=True),
        u'a': Element({u'href': Attribute(True), u'title': Attribute()},
                      set((None, u'strong', u'em')),
                      [(u'p', []), (u'li', [])], must_have_content=True),
        u'em': Element({u'title': Attribute()},
                       set((None, u'strong', u'b', u'a')),
                       [(u'p', []), (u'li', [])], must_have_content=True),
        u'strong': Element({u'title': Attribute()},
                           set((None, u'em', u'i', u'a')),
                           [(u'p', []), (u'li', [])], must_have_content=True),
        u'i': ReplacedElement(u'em', {u'title': Attribute()},
                              set((None, u'strong', u'b', u'a')),
                              [(u'p', []), (u'li', [])],
                              must_have_content=True),
        u'b': ReplacedElement(u'strong', {u'title': Attribute()},
                              set((None, u'em', u'i', u'a')),
                              [(u'p', []), (u'li', [])],
                              must_have_content=True),
        u'h1': Element({u'title': Attribute()}, set((None, u'br', u'em', u'a',
                                                     u'strong', u'img')),
                       must_have_content=True),
        u'h2': Element({u'title': Attribute()}, set((None, u'br', u'em', u'a',
                                                     u'strong', u'img')),
                       must_have_content=True),
        u'h3': Element({u'title': Attribute()}, set((None, u'br', u'em', u'a',
                                                     u'strong', u'img')),
                       must_have_content=True),
        u'h4': Element({u'title': Attribute()}, set((None, u'br', u'em', u'a',
                                                     u'strong', u'img')),
                       must_have_content=True),
        u'h5': Element({u'title': Attribute()}, set((None, u'br', u'em', u'a',
                                                     u'strong', u'img')),
                       must_have_content=True),
        u'h6': Element({u'title': Attribute()}, set((None, u'br', u'em', u'a',
                                                     u'strong', u'img')),
                       must_have_content=True),
    }
    root_can_contain = set((None, u'p', u'ul', u'ol', u'img', u'blockquote',
                            u'h1', u'h2', u'h3', u'h4', u'h5', u'h6',
                            u'a', u'em', u'strong', u'br', u'i', u'b'))
    text_can_create = [(u'p', []), (u'li', [])]
    
def sanitize_html(html, profile):
    sanitizer = HtmlSanitizer(profile)
    sanitizer.feed(html)
    sanitizer.close()
    return sanitizer.result.getvalue()
