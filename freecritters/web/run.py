# -*- coding: utf-8 -*-

from freecritters.web import app
from freecritters.config import Configuration
import sys

class EnvironAdderMiddleware(object):
    def __init__(self, wrapped, environ):
        self.wrapped = wrapped
        self.environ = environ
    
    def __call__(self, environ, start_response):
        environ.update(self.environ)
        return self.wrapped(environ, start_response)
        
def load_config():
    try:
        filename = sys.argv[1]
    except IndexError:
        sys.stdout.write('Need a config filename.\n')
        sys.exit(1)
    return Configuration.read_yaml_file(filename)
        
def run_dev():
    config = load_config()
    environ = {'freecritters.config': config}
    
    from colubrid import execute
    from freecritters.model import metadata

    execute(EnvironAdderMiddleware(app, environ), reload=True,
            hostname=config.http_hostname, port=config.http_port)

def run_fcgi():
    config = load_config()
    environ = {'freecritters.config': config}
    
    from flup.server.fcgi import WSGIServer
    WSGIServer(app, environ=environ).run()
