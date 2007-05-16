# -*- coding: utf-8 -*-

from colubrid import RegexApplication, HttpResponse, Request
from colubrid.server import StaticExports
from colubrid.exceptions import HttpException, AccessDenied
from sqlalchemy import create_session
import os
from freecritters import model
from freecritters.web import templates

class FreeCrittersRequest(Request):
    def __init__(self, environ, start_response, charset='utf-8'):
        super(FreeCrittersRequest, self).__init__(environ, start_response,
                                                  charset)
        self.config = environ['freecritters.config']
        self.sess = create_session(bind_to=self.config.db_engine)
        self.trans = self.sess.create_transaction()
        self._find_login()
    
    def _find_login(self):
        self.login = None
        if 'login_id' in self.cookies and 'login_code' in self.cookies:
            try:
                login_id = int(self.cookies['login_id'].value)
            except ValueError:
                return
            login = self.sess.query(model.Login).get(login_id)
            if login is None:
                return
            if login.code == self.cookies['login_code'].value.decode('ascii'):
                self.login = login
    
    def has_permission(self, permission):
        """Checks if the user has a given permission (identified as either a
        Permission object or a label) and returns True or False. None can also
        be used in place of a permission to check whether there is a logged-in
        user at all.
        """
        
        if self.login is None:
            return False
        if permission is None:
            return True
        else:
            return self.login.has_permission(permission)
        
    def check_permission(self, permission):
        """Checks if the user has a given permission (identified as either a
        Permission object or a label) and raises AccessDenied if not. None
        can also be used in place of a permission to check whether there
        is a logged-in user at all.
        """
        
        if not self.has_permission(permission):
            raise AccessDenied()
        
class FreeCrittersApplication(RegexApplication):
    charset = 'utf-8'
    urls = [
        ('^$', 'freecritters.web.home.home'),
        ('^register$', 'freecritters.web.register.register'),
        ('^login$', 'freecritters.web.login.login'),
        ('^logout$', 'freecritters.web.logout.logout'),
        ('^users/(.+)$', 'freecritters.web.profile.profile'),
        ('^editprofile$', 'freecritters.web.settings.edit_profile'),
        ('^subaccounts$', 'freecritters.web.settings.subaccount_list'),
        ('^mail$', 'freecritters.web.mail.inbox'),
        ('^mail/send$', 'freecritters.web.mail.send'),
        ('^mail/(\d+)$', 'freecritters.web.mail.conversation'),
        ('^mail/(\d+)/reply$', 'freecritters.web.mail.reply'),
        ('^mail/delete$', 'freecritters.web.mail.multi_delete'),
        ('^json/pre_mail_message$',
            'freecritters.web.mail.pre_mail_message_json')
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
    
    def process_http_exception(self, e):
        if isinstance(e, AccessDenied):
            return templates.factory.render('access_denied', self.request)
        else:
            return super(FreeCrittersApplication, self) \
                               .process_http_exception(e)
        
app = StaticExports(FreeCrittersApplication, { # Switch to the proper egg way!
    '/static': os.path.join(os.path.dirname(__file__), 'static')
})
