# -*- coding: utf-8 -*-

from colubrid import HttpResponse
from jinja import Template, Context, EggLoader
from jinja.exceptions import TemplateDoesNotExist
from jinja.lib import stdlib
from freecritters.web import links
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
                template = Template(name, self.loader)
                self._cache[name] = template
                return template
        else:
            return Template(name, self.loader, lib=self.lib)
    
    def global_context(self, req):
        '''Returns the global context dictionary, which is available to every
        template.
        '''
        
        if req.login is None:
            username = None
            money = None
            user_link = None
            new_mail = False
        else:
            username = req.login.user.username
            money = req.login.user.money
            user_link = links.user_link(req.login.user)
            new_mail = req.login.user.has_new_mail()
            
        return {u'fc': {u'site_name': req.config.site_name,
                        u'username': username, u'money': money,
                        u'user_link': user_link,
                        u'new_mail': new_mail}}
    
    def render(self, template, req, context=None):
        '''Renders a template into an HttpResponse. template can be either a
        jinja.Template or the name of one to be loaded. context should be a
        mapping which will be passed to the template as context, along with
        the global context.
        '''
        
        if not isinstance(template, Template):
            template = self.load_template(template)
        full_context = self.global_context(req)
        if context is not None:
            full_context.update(context)
        context_context = Context(full_context) # Could this line contain any
                                                # more instances of that word?
        return HttpResponse(template.render(context_context))
        
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

fclib = stdlib.clone()
fclib.register_filter('intformat', handle_intformat)
fclib.register_filter('datetime', handle_datetime)
loader = EggLoader('freecritters', 'web/templates',
                   charset='utf-8')
factory = TemplateFactory(loader, lib=fclib)
