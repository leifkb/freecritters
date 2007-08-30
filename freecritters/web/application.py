# -*- coding: utf-8 -*-

from colubrid import RegexApplication, HttpResponse, Request
from colubrid.server import StaticExports
from colubrid.exceptions import HttpException, AccessDenied
from sqlalchemy import create_session, Query
import os 
from freecritters.model import ctx, Login, Permission, User, Role, FormToken
from freecritters.web import templates
from base64 import b64decode

class FreeCrittersRequest(Request):
    def __init__(self, environ, start_response, charset='utf-8'):
        environ['SCRIPT_NAME'] = ''
        super(FreeCrittersRequest, self).__init__(environ, start_response,
                                                  charset)
        self.config = environ['freecritters.config']
        self.sess = ctx.current
        self.sess.bind = self.config.db_engine
        self.trans = self.sess.create_transaction()
        self._find_login()
    
    def _find_login(self):
        self.login = None
        self.user = None
        self.subaccount = None
        if 'login_id' in self.cookies and 'login_code' in self.cookies:
            try:
                login_id = int(self.cookies['login_id'].value)
            except ValueError:
                return
            login = Query(Login).get(login_id)
            if login is None:
                return
            if login.code == self.cookies['login_code'].value.decode('ascii'):
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
                subaccount = Query(Subaccount).get_by(user_id=user.user_id, name=subaccount_name)
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
        if not isinstance(permission, Permission):
            permission = Permission.find_label(permission)
        return permission.possessed_by(self.user, self.subaccount)
        
    def check_permission(self, permission):
        """Checks if the user has a given permission (identified as either a
        Permission object or a label) and raises AccessDenied if not. None
        can also be used in place of a permission to check whether there
        is a logged-in user at all.
        """
        
        if not self.has_permission(permission):
            raise AccessDenied()
    
    def check_permission_rss(self, permission):
        """Like check_permission, but suitable for a page containing RSS."""
        if not self.has_permission(permission):
            raise RSS401()
    
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
            new_mail = self.has_permission('view_mail') \
                       and self.user.has_new_mail()
            
        return {'fc': {'site_name': self.config.site_name,
                       'unformatted_username': unformatted_username,
                       'user_id': user_id,
                       'username': username,
                       'money': money,
                       'new_mail': new_mail,
                       'subaccount_name': subaccount_name,
                       'request': self}}
    
    def render_template_to_string(self, template, context=None, **kwargs):
        if context is None:
            context = {}
        context.update(self.global_context())
        context.update(kwargs)
        return templates.env.get_template(template).render(context)
    
    def render_template(self, template, context=None, **kwargs):
        return FreeCrittersResponse(self.render_template_to_string(template, context, **kwargs))
                        

class RSS401(HttpException):
    code = 401
        
class FreeCrittersApplication(RegexApplication):
    charset = 'utf-8'
    urls = [
        (r'^$', 'freecritters.web.home.home'),
        (r'^register$', 'freecritters.web.register.register'),
        (r'^login$', 'freecritters.web.login.login'),
        (r'^logout$', 'freecritters.web.logout.logout'),
        (r'^users/(.+)$', 'freecritters.web.profile.profile'),
        (r'^editprofile$', 'freecritters.web.settings.edit_profile'),
        (r'^subaccounts$', 'freecritters.web.settings.subaccount_list'),
        (r'^subaccounts/create$', 'freecritters.web.settings.create_subaccount'),
        (r'^subaccounts/(\d+)/edit$', 'freecritters.web.settings.edit_subaccount'),
        (r'^subaccounts/(\d+)/delete$', 'freecritters.web.settings.delete_subaccount'),
        (r'^subaccounts/(\d+)/change_password$', 'freecritters.web.settings.change_subaccount_password'),
        (r'^pictures/(\d+)(?:\.[a-zA-Z]+)?$', 'freecritters.web.pictures.picture'),
        (r'^pictures/(\d+)/([A-Za-z]+)(?:\.[a-zA-Z]+)?$', 'freecritters.web.pictures.picture'),
        (r'^mail$', 'freecritters.web.mail.inbox'),
        (r'^rss/mail\.rss$', 'freecritters.web.mail.inbox_rss'),
        (r'^mail/send$', 'freecritters.web.mail.send'),
        (r'^mail/(\d+)$', 'freecritters.web.mail.conversation'),
        (r'^mail/(\d+)/reply$', 'freecritters.web.mail.reply'),
        (r'^mail/delete$', 'freecritters.web.mail.multi_delete'),
        (r'^json/pre_mail_message$',
            'freecritters.web.mail.pre_mail_message_json'),
        (r'^pets/images/(\d+)/(\d+)/([0-9A-F]{6})(?:\.[a-zA-Z]+)?$', 'freecritters.web.pets.pet_image'),
        (r'^pets/create/(\d+)$', 'freecritters.web.pets.create_pet'),
        (r'^pets$', 'freecritters.web.pets.pet_list'),
        (r'^pets/create$', 'freecritters.web.pets.species_list')
    ]
    
    def __init__(self, environ, start_response,
                 request_class=FreeCrittersRequest):
        super(FreeCrittersApplication, self).__init__(environ, start_response,
                                                      request_class)
    
    def __iter__(self):
        # We're doing this here instead of in process_request because
        # process_http_exception wants an open session too.
        try:
            try:
                response = super(FreeCrittersApplication, self).__iter__()
            except:
                self.request.trans.rollback()
                raise
            else:
                self.request.trans.commit()
            return response
        finally:
            self.request.sess.close()
            del ctx.current
    
    def process_http_exception(self, e):
        if isinstance(e, AccessDenied):
            return FreeCrittersResponse(
                self.request.render_template_to_string('access_denied.html'),
                status=e.code
            )
        elif isinstance(e, RSS401):
            return FreeCrittersResponse(
                self.request.render_template_to_string('access_denied.rss'),
                [('Content-Type', 'application/rss+xml'),
                 ('WWW-Authenticate', 'Basic realm="' + self.request.config.site_name.encode('utf8') + '"')],
                status=e.code
            )
        else:
            return super(FreeCrittersApplication, self).process_http_exception(e)
      
class FreeCrittersResponse(HttpResponse):
    """HttpResponse with some defaults."""
    def __init__(self, *args, **kwargs):
        HttpResponse.__init__(self, *args, **kwargs)
        self['Vary'] = 'Cookie'
        
    
app = StaticExports(FreeCrittersApplication, { # Switch to the proper egg way!
    '/static': os.path.join(os.path.dirname(__file__), 'static')
})
