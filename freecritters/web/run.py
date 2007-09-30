# -*- coding: utf-8 -*-

from freecritters.web import app
from freecritters.config import config_from_yaml
import sys

class EnvironAdderMiddleware(object):
    def __init__(self, wrapped, environ):
        self.wrapped = wrapped
        self.environ = environ
    
    def __call__(self, environ, start_response):
        environ.update(self.environ)
        return self.wrapped(environ, start_response)
        
def _load_config():
    try:
        filename = sys.argv[1]
    except IndexError:
        sys.stdout.write('Need a config filename.\n')
        sys.exit(1)
    return config_from_yaml(filename)
        
def run_dev():
    config = _load_config()
    environ = {'freecritters.config': config}
    
    from colubrid import execute

    execute(EnvironAdderMiddleware(app, environ), reload=True,
            hostname=config.http.hostname, port=config.http.port)

def run_fcgi():
    config = _load_config()
    environ = {'freecritters.config': config}
    
    from flup.server.fcgi import WSGIServer
    WSGIServer(app, environ=environ).run()
