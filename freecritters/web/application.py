# -*- coding: utf-8 -*-

from colubrid import RegexApplication, HttpResponse, Request
from colubrid.server import StaticExports
from colubrid.exceptions import HttpException
from sqlalchemy import create_session
import os

class FreeCrittersRequest(Request):
    def __init__(self, environ, start_response, charset='utf-8'):
        super(FreeCrittersRequest, self).__init__(environ, start_response,
                                                  charset)
        self.config = environ['freecritters.config']
        self.sess = create_session(bind_to=self.config.db_engine)
        self.trans = self.sess.create_transaction()
        
class FreeCrittersApplication(RegexApplication):
    charset = 'utf-8'
    urls = [
        ('^$', 'freecritters.web.foo.foo'),
    ]
    
    def __init__(self, environ, start_response,
                 request_class=FreeCrittersRequest):
        super(FreeCrittersApplication, self).__init__(environ, start_response,
                                                      request_class)
    
    def process_request(self):
        try:
            try:
                response = super(FreeCrittersApplication, self).process_request()
            except HttpException:
                self.request.trans.commit()
                raise
            except:
                self.request.trans.rollback()
                raise
            else:
                self.request.trans.commit()
        finally:
            self.request.sess.close()
        return response

        
app = StaticExports(FreeCrittersApplication, { # Switch to the proper egg way!
    '/static': os.path.join(os.path.dirname(__file__), 'static')
})
