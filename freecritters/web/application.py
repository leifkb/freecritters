# -*- coding: utf-8 -*-

from werkzeug.wrappers import BaseRequest, BaseResponse
from werkzeug.routing import Map, Rule
from werkzeug import routing
from werkzeug.utils import SharedDataMiddleware
from storm.locals import Store
import os 
from freecritters.model import Session, Login, Permission, User, Role, FormToken, \
                               SpecialGroupPermission, StandardGroupPermission
from freecritters.web import templates
from freecritters.web.exceptions import Redirect302, Error403, Error401RSS, \
                                        Error404
from freecritters.web.urls import urls
from base64 import b64decode

class Request(BaseRequest):
    charset = 'utf-8'
    
    def __init__(self, environ, url_adapter):
        super(Request, self).__init__(environ)
        self.config = environ['freecritters.config']
        Session().bind = self.config.database.engine
        self.url_adapter = url_adapter
        self._find_login()
    
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
            if u'@' in username:
                username, subaccount_name = username.split(u'@', 1)
            else:
                subaccount_name = None                            
            user = User.find_user(username)
            if user is None:
                return
            if subaccount_name is not None:
                subaccount = Subaccount.filter_by(user_id=user.user_id, name=subaccount_name).one()
                if subaccount is None:
                    return
                authenticator = subaccount
            else:
                subaccount = None
                authenticator = user
            if authenticator.check_password(password):
                self.user = user
                self.subaccount = subaccount
            
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
        membership = self.user.find_group_membership(group)
        if membership is None:
            return False
        if permission is None:
            return True
        return membership.role.has_permission(permission)
                
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
                       'url_for': self.url_for}}
    
    def render_template_to_string(self, template, context=None, **kwargs):
        if context is None:
            context = {}
        context.update(self.global_context())
        context.update(kwargs)
        return templates.env.get_template(template).render(context)
    
    def render_template(self, template, context=None, **kwargs):
        return Response(self.render_template_to_string(template, context, **kwargs))                        
    
    def url_for(self, name, **args):
        return self.url_adapter.build(name, args)
        
class Response(BaseResponse):
    charset = 'utf-8'
    default_mimetype = 'text/html'

    def __init__(self, *args, **kwargs):
        super(Response, self).__init__(*args, **kwargs)
        self.headers['Vary'] = 'Cookie'

def _generate_response(req, url_adapter):
    try:
        name, args = url_adapter.match(req.path)
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
        response = function(req, **args)
        if response is None:
            raise Error404()
    except (routing.NotFound, Error404):
        response = req.render_template('errors/404.html')
        response.status = 404
    except (routing.RequestRedirect, Redirect302), e:
        response = req.render_template('errors/redirect.html',
                                       new_url=e.new_url)
        response.status = 302
        response.headers['Location'] = e.new_url
    except Error403:
        response = req.render_template('errors/403.html')
        response.status = 403
    except Error401RSS:
        response = req.render_template('errors/401.rss')
        response.status = 401
        response.headers['Content-Type'] = 'application/rss+xml'
        response.headers['WWW-Authenticate'] = 'Basic realm="' + self.request.config.site.name.encode('utf8') + '"'
    return response

def application(environ, start_response):
    if not environ['PATH_INFO']:
        environ['PATH_INFO'] = environ['SCRIPT_NAME']
        environ['SCRIPT_NAME'] = ''
    url_adapter = urls.bind_to_environ(environ)
    req = Request(environ, url_adapter)
    try:
        try:
            response = _generate_response(req, url_adapter)
        except Exception, e:
            Session().rollback()
            raise
        else:
            Session().commit()
        return response(environ, start_response)
    finally:
        Session.remove()
    
application = SharedDataMiddleware(application, {
    '/static': os.path.join(os.path.dirname(__file__), 'static')
})