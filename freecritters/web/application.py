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
from base64 import b64decode
from urllib import urlencode

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
            login = Login.query.get(login_id)
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
            response = self.render_template('errors/404.html')
            response.status_code = 404
        except (routing.RequestRedirect, Redirect302), e:
            response = self.render_template('errors/redirect.html',
                                            new_url=e.new_url)
            response.status_code = 302
            response.headers['Location'] = e.new_url
        except Error304:
            response = Response('')
            response.status_code = 304
        except Error403:
            response = self.render_template('errors/403.html')
            response.status_code = 403
        except Error401RSS:
            response = self.render_template('errors/401.rss', mimetype='application/rss+xml')
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
        return membership.role.has_permission(permission)
    
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
        
    def global_context(self):
        '''Returns the global context dictionary, which is available to every
        template.
        '''
        if self.user is None:
            username = None
            unformatted_username = None
            user_id = None
            subaccount_name = None
            money = None
            user_link = None
            new_mail = False
        else:
            username = self.user.username
            unformatted_username = self.user.unformatted_username
            user_id = self.user.user_id
            if self.subaccount is not None:
                subaccount_name = req.subaccount.name
            else:
                subaccount_name = None
            money = self.user.money
            new_mail = self.has_permission(u'view_mail') \
                       and self.user.has_new_mail()
            
        return {'fc': {'site_name': self.config.site.name,
                       'unformatted_username': unformatted_username,
                       'user_id': user_id,
                       'username': username,
                       'money': money,
                       'new_mail': new_mail,
                       'subaccount_name': subaccount_name,
                       'request': self,
                       'url': self.url_for,
                       'url_routing_js': generate_adapter(self.url_adapter)}}
    
    def render_template_to_string(self, template, context=None, **kwargs):
        if context is not None:
            kwargs.update(context)
        kwargs.update(self.global_context())
        return templates.env.get_template(template).render(kwargs)
    
    def render_template(self, template, context=None, mimetype=None, **kwargs):
        return Response(self.render_template_to_string(template, context, **kwargs), mimetype=mimetype)                        
    
    def url_for(self, endpoint, args=None, absolute=False, **kwargs):
        if args is not None:
            kwargs.update(args)
        return self.url_adapter.build(endpoint, kwargs, absolute)
    
    def redirect(self, endpoint, args=None, **kwargs):
        if args is not None:
            kwargs.update(args)
        raise Redirect302(self.url_for(endpoint, kwargs, True))
    
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