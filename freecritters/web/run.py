# -*- coding: utf-8 -*-

from freecritters.web.application import application
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

def wrap_app(config, app):
    if config.debug.tracebacks:
        from werkzeug.debug import DebuggedApplication
        app = DebuggedApplication(app, evalex=config.debug.evalex)
    return app

def run_dev():
    config = load_config()
    environ = make_environ(config)
    
    from werkzeug.serving import run_simple
    
    app = wrap_app(config, application)
    run_simple(config.http.hostname, config.http.port,
               EnvironAdderMiddleware(app, environ),
               use_reloader=config.http.reload)


def run_fcgi():
    config = load_config()
    environ = make_environ(config)
    
    from flup.server.fcgi import WSGIServer
    app = wrap_app(config, application)
    WSGIServer(app, environ=environ, debug=False).run()