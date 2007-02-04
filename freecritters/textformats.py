# -*- coding: utf-8 -*-

from freecritters.htmlsanitize import sanitize_html, StandardProfile, \
                                      StandardProfile2
from HTMLParser import HTMLParseError
from xml.sax.saxutils import escape
import re

text_formats = [
    (u'plain', u'Plain text'),
    (u'html', u'HTML'),
    (u'html_auto', u'HTML with automatic line breaks')
]

_line_break_re = re.compile(u'((?:\r\n|\r|\n)+|[^\r\n]+)')

def plain_text(text, max_lines=None):
    result = []
    open_paragraph = False
    lines = 0
    for part in _line_break_re.findall(text):
        if part[0] in u'\r\n':
            if not open_paragraph or (result and result[-1] == u'<p>'):
                continue
            result.append(part)
            if max_lines is not None and lines >= max_lines:
                continue
            if part in (u'\r\n', u'\r', u'\n'):
                lines += 1
                result.append(u'<br>')
            else:
                result.append(u'</p>')
                open_paragraph = False
        else:
            if not part.isspace() and not open_paragraph:
                result.append(u'<p>')
                lines += 1
                open_paragraph = True
            result.append(escape(part))
    if open_paragraph:
        result.append(u'</p>')
    return u''.join(result)
    
def formatted_text_to_html(text, format):
    if format == u'plain':
        return plain_text(text)
    try:
        if format == 'html':
            return sanitize_html(text, StandardProfile2)
        else: # html_auto
            return sanitize_html(text, StandardProfile)
    except HTMLParseError, e:
        raise ValueError(str(e))
