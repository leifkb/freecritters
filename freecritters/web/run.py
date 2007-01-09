# -*- coding: utf-8 -*-

from freecritters.web import app

class EnvironAdderMiddleware(object):
    def __init__(self, wrapped, environ):
        self.wrapped = wrapped
        self.environ = environ
    
    def __call__(self, environ, start_response):
        environ.update(self.environ)
        return self.wrapped(environ, start_response)
        
def run_dev():
    from freecritters.web import templates
    templates.cache = False
    from colubrid import execute
    execute(EnvironAdderMiddleware(app, {'freecritters.foo': 'bar'}), reload=True)

def run_fcgi():
    from flup.server.fcgi import WSGIServer
    WSGIServer(app).run()
