# -*- coding: utf-8 -*-

"""Utility stuff."""

import simplejson
from werkzeug.utils import get_current_url
from urlparse import urljoin
from datetime import datetime
import re

def returns_json(fun):
    """Decorator which wraps a function's return value in a Werkzeug
    HTTP response containing a JSON string.
    """
    from freecritters.web.application import Response
    def wrapper(*args, **kwargs):
        return Response(simplejson.dumps(fun(*args, **kwargs)),
                        mimetype='application/json; charset=utf-8')
    return wrapper

_wkdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep',
           'Oct', 'Nov', 'Dec']
_weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Friday', 'Saturday', 'Sunday']
_rfc1123_date = re.compile(r'^(?:%s), (\d{2}) (%s) (\d{4}) (\d{2}):(\d{2}):(\d{2}) GMT$' % ('|'.join(_wkdays), '|'.join(_months)))
_rfc850_date = re.compile(r'^(?:%s), (\d{2})-(%s)-(\d{2}) (\d{2}):(\d{2}):(\d{2}) GMT' % ('|'.join(_weekdays), '|'.join(_months)))
_asctime_date = re.compile(r'^(?:%s) (%s) (\d{2}| \d) (\d{2}):(\d{2}):(\d{2}) (\d{4})' % ('|'.join(_wkdays), '|'.join(_months)))

def http_date(date):
    day_name = _wkdays[date.weekday()]
    month_name = _months[date.month-1]
    return '%s, %02d %s %s %02d:%02d:%02d GMT' % \
        (day_name, date.day, month_name, date.year, date.hour, date.minute,
         date.second)

def parse_http_date(date):
    match = _rfc1123_date.search(date)
    if match is not None:
        day = int(match.group(1))
        month = _months.index(match.group(2)) + 1
        year = int(match.group(3))
        hour = int(match.group(4))
        minute = int(match.group(5))
        second = int(match.group(6))
        return datetime(year, month, day, hour, minute, second)
    match = _rfc850_date.search(date)
    if match is not None:
        day = int(match.group(1))
        month = _months.index(match.group(2)) + 1
        year = int(match.group(3))
        if year > 20: # I have no idea what the correct logic is here
            year += 1900
        else:
            year += 2000
        hour = int(match.group(4))
        minute = int(match.group(5))
        second = int(match.group(6))
        return datetime(year, month, day, hour, minute, second)
    match = _asctime_date.search(date)
    if match is not None:
        month = _months.index(match.group(1)) + 1
        day = int(match.group(2).strip())
        hour = int(match.group(3))
        minute = int(match.group(4))
        second = int(match.group(5))
        year = int(match.group(6))
        return datetime(year, month, day, hour, minute, second)
    raise ValueError("Can't parse date: %r" % date)
        
def absolute_url(req, url):
    return urljoin(get_current_url(req.environ), url)

class LazyProperty(object):
    """Property that is lazyily initialized by calling a method."""
    
    def __init__(self, attr, method):
        self.attr = attr
        self.method = method
    
    def __get__(self, obj, type=None):
        if obj is None:
            return self
        try:
            return getattr(obj, self.attr)
        except AttributeError:
            getattr(obj, self.method)()
            return getattr(obj, self.attr)
    
    def __set__(self, obj, value):
        setattr(obj, self.attr, value)