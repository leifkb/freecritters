# -*- coding: utf-8 -*-

from freecritters.web.application import FreeCrittersResponse
from jinja import Template, Context, EggLoader
from jinja.exceptions import TemplateDoesNotExist
from jinja.lib import stdlib
from freecritters.web import links
from freecritters.web.util import absolute_url
from datetime import datetime

class TemplateFactory(object):
    def __init__(self, loader, use_cache=True, lib=stdlib):
        self.loader = loader
        self._cache = {}
        self.use_cache = use_cache
        self.lib = lib
        
    def load_template(self, name):
        '''Loads a template from the loader. If there's a cached copy, it is
        returned. Raises jinja.exceptions.TemplateDoesNotExist if the template
        can't be found.
        '''
        
        # XXX This should be thread-safe, but I'm not completely sure whether
        # XXX that's just a CPython implementation detail.
        if self.use_cache:
            try:
                return self._cache[name]
            except KeyError:
                template = Template(name, self.loader, lib=self.lib)
                self._cache[name] = template
                return template
        else:
            return Template(name, self.loader, lib=self.lib)
    
    def global_context(self, req):
        '''Returns the global context dictionary, which is available to every
        template.
        '''
        
        if req.user is None:
            username = None
            subaccount_name = None
            money = None
            user_link = None
            new_mail = False
        else:
            username = req.user.username
            if req.subaccount is not None:
                subaccount_name = req.subaccount.name
            else:
                subaccount_name = None
            money = req.user.money
            user_link = links.user_link(req.user)
            new_mail = req.has_permission('view_mail') \
                       and req.user.has_new_mail()
            
        return {u'fc': {u'site_name': req.config.site_name,
                        u'username': username, u'money': money,
                        u'user_link': user_link,
                        u'new_mail': new_mail,
                        u'subaccount_name': subaccount_name,
                        u'request': req}}
    
    def render_string(self, template, req, context=None):
        """Renders a template into a string. template can be either a
        jinja.Template or the name of one to be loaded. context should be a
        mapping which will be passed to the template as context, along with
        the global context.
        """
        if not isinstance(template, Template):
            template = self.load_template(template)
        full_context = self.global_context(req)
        if context is not None:
            full_context.update(context)
        context_context = Context(full_context) # Could this line contain any
                                                # more instances of that word?
        return template.render(context_context)
    
    def render(self, template, req, context=None):
        """Renders a template into an HttpResponse. template can be either a
        jinja.Template or the name of one to be loaded. context should be a
        mapping which will be passed to the template as context, along with
        the global context.
        """
        return FreeCrittersResponse(self.render_string(template, req, context))
        
def handle_intformat(n, context):    
    n = unicode(n)
    groups = []
    if len(n) % 3 != 0:
        groups.append(n[:len(n) % 3])
    for i in xrange(len(n) % 3, len(n), 3):
        groups.append(n[i:i+3])
    return u'\N{NO-BREAK SPACE}'.join(groups)

def handle_datetime(t, context, sep=u'\N{NO-BREAK SPACE}'):
    t = datetime(t.year, t.month, t.day, t.hour, t.minute, t.second)
    return t.isoformat('T').decode('ascii').replace('T', sep)

def handle_escapequotes(text, context):
    text = unicode(text)
    text = text.replace(u'&', u'&amp;')
    text = text.replace(u'<', u'&lt;')
    text = text.replace(u'>', u'&gt;')
    text = text.replace(u'"', u'&quot;')
    return text
   
def handle_eq(text, context):
    return handle_escapequotes(text, context)

def handle_absolute_url(text, context):
    return absolute_url(context[u'fc'][u'request'], text)

def handle_rsstimestamp(ts, context):
    return ts.strftime('%a, %d %B %Y %H:%M:%S GMT')

fclib = stdlib.clone()
fclib.register_filter('intformat', handle_intformat)
fclib.register_filter('datetime', handle_datetime)
fclib.register_filter('escapequotes', handle_escapequotes)
fclib.register_filter('eq', handle_eq)
fclib.register_filter('absolute_url', handle_absolute_url)
fclib.register_filter('rsstimestamp', handle_rsstimestamp)
loader = EggLoader('freecritters', 'web/templates',
                   charset='utf-8')
factory = TemplateFactory(loader, lib=fclib)