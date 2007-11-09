# -*- coding: utf-8 -*-

from freecritters.web import application
from freecritters.config import config_from_yaml
from datetime import datetime
import sys

class EnvironAdderMiddleware(object):
    def __init__(self, wrapped, environ):
        self.wrapped = wrapped
        self.environ = environ
    
    def __call__(self, environ, start_response):
        environ.update(self.environ)
        return self.wrapped(environ, start_response)

def make_environ(config):
    return {'freecritters.config': config,
            'freecritters.startup': datetime.utcnow()}

def load_config():
    try:
        filename = sys.argv[1]
    except IndexError:
        sys.stdout.write('Need a config filename.\n')
        sys.exit(1)
    return config_from_yaml(filename)
        
def run_dev():
    config = _load_config()
    environ = {'freecritters.config': config}
    
    from werkzeug.serving import run_simple
    
    try:
        run_simple(config.http.hostname, config.http.port,
                   EnvironAdderMiddleware(application, environ), use_reloader=True)
    except Exception, e:
        print e

def run_fcgi():
    environ = make_environ(load_config())
    
    from flup.server.fcgi import WSGIServer
    WSGIServer(application, environ=environ).run()
