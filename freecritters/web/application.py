# -*- coding: utf-8 -*-

from werkzeug.wrappers import BaseRequest, BaseResponse
from werkzeug.routing import Map, Rule
from werkzeug import routing
from werkzeug.contrib.jsrouting import generate_adapter
from werkzeug.utils import SharedDataMiddleware
import os 
from freecritters.model import Session, Login, Permission, User, Role, FormToken, \
                               SpecialGroupPermission, StandardGroupPermission
from freecritters.web import templates
from freecritters.web.exceptions import Redirect302, Error304, Error403, \
                                        Error401RSS, Error404
from freecritters.web.urls import urls
from freecritters.web.util import absolute_url, LazyProperty, http_date, \
                                  parse_http_date
from freecritters.web.globals import fc, global_manager
from base64 import b64decode
from urllib import urlencode
from sqlalchemy.orm import eagerload

class Request(BaseRequest):
    charset = 'utf-8'
    
    def __init__(self, environ, url_adapter):
        super(Request, self).__init__(environ)
        self.config = environ['freecritters.config']
        Session().bind = self.config.database.engine
        self.url_adapter = url_adapter
        self.endpoint = None
        self.routing_args = None
    
    login = LazyProperty('_login', '_find_login')
    user = LazyProperty('_user', '_find_login')
    subaccount = LazyProperty('_subaccount', '_find_login')
    
    def _find_login(self):
        self.login = None
        self.user = None
        self.subaccount = None
        if 'login_id' in self.cookies and 'login_code' in self.cookies:
            try:
                login_id = int(self.cookies['login_id'])
            except ValueError:
                return
            login = Login.query.options(
                eagerload('user'),
                eagerload('user.role'),
                eagerload('subaccount')
            ).get(login_id)
            if login is None:
                return
            if login.code == self.cookies['login_code']:
                self.login = login
                self.user = login.user
                self.subaccount = login.subaccount
        elif 'HTTP_AUTHORIZATION' in self.environ and self.environ['HTTP_AUTHORIZATION'].startswith('Basic '):
            base64ed = self.environ['HTTP_AUTHORIZATION'][6:]
            try:
                unbase64ed = b64decode(base64ed)
                username, password = unbase64ed.split(':', 1)
                username = username.decode('utf8')
                password = password.decode('utf8')
            except (TypeError, ValueError, UnicodeDecodeError):
                return
            if u'/' in username:
                username, subaccount_name = username.split(u'/', 1)
            else:
                subaccount_name = None                            
            user = User.find_user(username)
            if user is None:
                return
            if subaccount_name is not None:
                subaccount = user.subaccounts.filter_by(name=subaccount_name).first()
                if subaccount is None:
                    return
                authenticator = subaccount
            else:
                subaccount = None
                authenticator = user
            if authenticator.check_password(password):
                self.user = user
                self.subaccount = subaccount
    
    @property
    def url_routing_js(self):
        return generate_adapter(self.url_adapter)
    
    def generate_response(self):
        try:
            name, args = self.url_adapter.match(self.path)
            self.endpoint = name
            self.routing_args = args
            parts = name.rsplit('.', 1)
            if len(parts) == 1:
                module_name = function_name = parts[0]
            else:
                module_name, function_name = parts
            module_name = 'freecritters.web.' + module_name
            module = __import__(module_name, None, None, [''])
            function = getattr(module, function_name)
            for key in args:
                if key.endswith('__'):
                    del args[key]
            response = function(self, **args)
            if response is None:
                raise Error404()
        except routing.BuildError:
            # Subclass of NotFound; would be caught by the next exception
            # handler otherwise
            raise
        except (routing.NotFound, Error404), e:
            response = self.render_template('errors/404.mako')
            response.status_code = 404
        except (routing.RequestRedirect, Redirect302), e:
            response = self.render_template('errors/redirect.mako',
                                            new_url=e.new_url)
            response.status_code = 302
            response.headers['Location'] = e.new_url
        except Error304:
            response = Response('')
            response.status_code = 304
        except Error403:
            response = self.render_template('errors/403.mako')
            response.status_code = 403
        except Error401RSS:
            response = self.render_template('errors/401_rss.mako', mimetype='application/rss+xml')
            response.status_code = 401
            response.headers['WWW-Authenticate'] = 'Basic realm="' + self.config.site.name.encode('utf8') + '"'
        return response
    
    def has_permission(self, permission):
        """Checks if the user has a given permission (identified as either a
        Permission object or a label) and returns True or False. None can also
        be used in place of a permission to check whether there is a logged-in
        user at all.
        """
        
        if self.user is None:
            return False
        if permission is None:
            return True
        if isinstance(permission, basestring):
            permission = Permission.find_label(permission)
        return permission.possessed_by(self.user, self.subaccount)
        
    def check_permission(self, permission):
        """Checks if the user has a given permission (identified as either a
        Permission object or a label) and raises Error403 if not. None
        can also be used in place of a permission to check whether there
        is a logged-in user at all.
        """
        
        if not self.has_permission(permission):
            raise Error403()
    
    def check_permission_rss(self, permission):
        """Like check_permission, but suitable for a page containing RSS."""
        if not self.has_permission(permission):
            raise Error401RSS()
    
    def has_group_permission(self, group, permission):
        if self.user is None:
            return False
        if not self.has_permission(u'groups'):
            return False
        membership = self.user.group_memberships.filter_by(group_id=group.group_id).first()
        if membership is None:
            return False
        if permission is None:
            return True
        return membership.has_permission(permission)
    
    def check_group_permission(self, group, permission):
        if not self.has_group_permission(group, permission):
            raise Error403()
    
    def check_group_permission_rss(self, group, permission):
        if not self.has_group_permission(group, permission):
            raise Error401RSS()
       
    def form_token(self):
        return self.form_token_object().token

    def form_token_object(self):
        return FormToken.form_token_for(self.user, self.subaccount)
    
    def render_template_to_string(self, *args, **kwargs):
        template = args[0]
        args = args[1:]
        return templates.loader.get_template(template).render(*args, **kwargs)
    
    def render_template_to_unicode(self, *args, **kwargs):
        template = args[0]
        args = args[1:]
        return templates.loader.get_template(template).render_unicode(*args, **kwargs)
    
    def render_template(self, *args, **kwargs):
        return Response(self.render_template_to_string(*args, **kwargs))                        
    
    def url_for(self, endpoint, args=None, absolute=False, **kwargs):
        if args is not None:
            kwargs.update(args)
        return self.url_adapter.build(endpoint, kwargs, absolute)
    
    def redirect(self, endpoint, args=None, fragment=None, **kwargs):
        if args is not None:
            kwargs.update(args)
        url = self.url_for(endpoint, kwargs, True)
        if fragment is not None:
            url += '#%s' % fragment
        raise Redirect302(url)
    
    def check_modified(self, modified):
        if modified is None:
            return
        modified = modified.replace(microsecond=0)
        try:
            if_modified_since = parse_http_date(self.environ['HTTP_IF_MODIFIED_SINCE'])
        except (KeyError, ValueError):
            return
        if modified <= if_modified_since:
            raise Error304()
            
    def urlencode(self, args):
        return urlencode([(key, val.encode(self.charset)) for key, val in args])
    
class Response(BaseResponse):
    charset = 'utf-8'
    default_mimetype = 'text/html'

    def __init__(self, *args, **kwargs):
        super(Response, self).__init__(*args, **kwargs)
        self.headers['Vary'] = 'Cookie'
    
    def last_modified(self, modified, must_revalidate=True):
        if modified is not None:
            self.headers['Last-Modified'] = http_date(modified)
        if must_revalidate:
            self.headers['Cache-Control'] = 'max-age=0, must-revalidate'
        return self
    
def application(environ, start_response):
    if not environ['PATH_INFO']:
        environ['PATH_INFO'] = environ['SCRIPT_NAME']
        environ['SCRIPT_NAME'] = ''
    url_adapter = urls.bind_to_environ(environ)
    req = Request(environ, url_adapter)
    fc.req = req
    fc.url = req.url_for
    fc.config = req.config
    try:
        try:
            response = req.generate_response()
        except Exception, e:
            Session().rollback()
            raise
        else:
            Session().commit()
        return response(environ, start_response)
    finally:
        Session.remove()

application = global_manager.make_middleware(application)