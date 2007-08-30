# -*- coding: utf-8 -*-

from jinja import Environment, PackageLoader
from jinja.filters import stringfilter, simplefilter
from freecritters.web.util import absolute_url
from freecritters.web.tabs import Tabs
from datetime import datetime

env = Environment(loader=PackageLoader('freecritters', 'web/templates'))

@stringfilter
def do_intformat(n):    
    n = unicode(n)
    groups = []
    if len(n) % 3 != 0:
        groups.append(n[:len(n) % 3])
    for i in xrange(len(n) % 3, len(n), 3):
        groups.append(n[i:i+3])
    return u'\N{NO-BREAK SPACE}'.join(groups)
env.filters['intformat'] = do_intformat

@simplefilter
def do_datetime(t, sep=u'\N{NO-BREAK SPACE}'):
    t = datetime(t.year, t.month, t.day, t.hour, t.minute, t.second)
    return t.isoformat('T').decode('ascii').replace('T', sep)
env.filters['datetime'] = do_datetime

def do_absolute_url():
    def wrapped(env, context, text):
        return absolute_url(context['fc']['request'], text)
    return wrapped
env.filters['absolute_url'] = do_absolute_url

@simplefilter
def do_rsstimestamp(ts):
    return ts.strftime('%a, %d %B %Y %H:%M:%S GMT')
env.filters['rsstimestamp'] = do_rsstimestamp

env.globals['Tabs'] = Tabs