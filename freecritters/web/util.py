# -*- coding: utf-8 -*-

"""Utility stuff."""

import simplejson

def returns_json(fun):
    """Decorator which wraps a function's return value in a Colubrid
    HTTP response containing a JSON string.
    """
    def wrapper(*args, **kwargs):
        return FreeCrittersResponse(simplejson.dumps(fun(*args, **kwargs)),
                                    [('Content-Type', 'application/json')])
    return wrapper

# %a and %b are locale-dependent
_day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
_month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep',
                'Oct', 'Nov', 'Dec']
    
def http_date(date):
    day_name = _day_names[date.weekday()]
    month_name = _month_names[date.month-1]
    return '%s, %02d %s %s %02d:%02d:%02d GMT' % \
        (day_name, date.day, month_name, date.year, date.hour, date.minute,
         date.second)