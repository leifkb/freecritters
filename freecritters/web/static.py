from os import path, stat
from mimetypes import guess_type
from freecritters.web.util import http_date
from datetime import datetime

class StaticServer(object):
    def __init__(self, path, block_size=10240):
        self.path = path
        self.block_size = block_size
    
    def __call__(self, req, fn):
        prefix = path.abspath(self.path)
        full_path = path.abspath(path.join(self.path, fn))
        if full_path != prefix and not full_path.startswith(prefix + path.sep):
            return None
        
        if not path.isfile(full_path):
            return None
        
        def wsgi_responder(environ, start_response):
            mime_type, encoding = guess_type(full_path)
            if mime_type is None:
                mime_type = 'application/octet-stream'
            
            if mime_type.startswith('text/'):
                mime_type += '; charset=utf-8'
            
            info = stat(full_path)
            last_modified = datetime.utcfromtimestamp(info.st_mtime)
            if http_date(last_modified) == environ.get('HTTP_IF_MODIFIED_SINCE'):
                start_response('304 Not Modified', [])
                return ''
            headers = [('Content-Type', mime_type),
                       ('Content-Length', str(info.st_size)),
                       ('Last-Modified', http_date(last_modified))]
            if encoding is not None:
                headers.append(('Content-Encoding', encoding))
            
            start_response('200 OK', headers)
            f = open(full_path, 'rb')
            if 'wsgi.file_wrapper' in environ:
                return environ['wsgi.file_wrapper'](f, self.block_size)
            else:
                return iter(lambda: f.read(self.block_size), '')
        
        return wsgi_responder

static = StaticServer(path.join(path.dirname(__file__), 'static'))