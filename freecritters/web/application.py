# -*- coding: utf-8 -*-

from colubrid import RegexApplication, HttpResponse, Request

class FreeCrittersRequest(Request):
    def __init__(self, environ, start_response, charset='utf-8'):
        super(FreeCrittersRequest, self).__init__(environ, start_response,
                                                  charset)
        self.config = environ['freecritters.config']
        self.db
    
class FreeCrittersApplication(RegexApplication):
    charset = 'utf-8'
    urls = [
        ('^hello$', 'freecritters.web.foo.foo'),
        ('^hello/(.+)$', 'freecritters.web.foo.foo'),
    ]
    
    def __init__(self, environ, start_response,
                 request_class=FreeCrittersRequest):
        super(FreeCrittersApplication, self).__init__(environ, start_response,
                                                      request_class)
        
app = FreeCrittersApplication
