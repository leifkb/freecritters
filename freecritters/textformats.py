# -*- coding: utf-8 -*-

from userhtml import sanitize_html
from HTMLParser import HTMLParseError
from xml.sax.saxutils import escape
import re

_line_break_re = re.compile(u'((?:\r\n|\r|\n)+|[^\r\n]+)')

def render_plain_text(text, max_lines=None):
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
    
def render_html(data):
    try:
        return sanitize_html(data)
    except HTMLParseError, e:
        raise ValueError(str(e))