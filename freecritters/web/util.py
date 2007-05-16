# -*- coding: utf-8 -*-

"""Utility stuff."""

from urlparse import urljoin

try:
    from wsgiref.util import request_uri as reconstruct_url
except ImportError:
    from urllib import quote
    
    def reconstruct_url(environ):
        url = environ['wsgi.url_scheme']+'://'

        if environ.get('HTTP_HOST'):
            url += environ['HTTP_HOST']
        else:
            url += environ['SERVER_NAME']
        
            if environ['wsgi.url_scheme'] == 'https':
                if environ['SERVER_PORT'] != '443':
                   url += ':' + environ['SERVER_PORT']
            else:
                if environ['SERVER_PORT'] != '80':
                   url += ':' + environ['SERVER_PORT']
        
        url += quote(environ.get('SCRIPT_NAME',''))
        url += quote(environ.get('PATH_INFO',''))
        if environ.get('QUERY_STRING'):
            url += '?' + environ['QUERY_STRING'] 
        return url

def absolute_url(req, url):
    return urljoin(reconstruct_url(req.environ), url)

def redirect(req, exc, url):
    raise exc(absolute_url(req, url))
