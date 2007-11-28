# -*- coding: utf-8 -*-

from math import ceil
from urllib import urlencode

class Paginator(object):
    def __init__(self, page_size=25, argument='page'):
        self.page_size = page_size
        self.argument = 'page'
        
    def __call__(self, req, query, row_count=None):
        if row_count is None:
            row_count = query.count()
        page_count = max(1, int(ceil(float(row_count) / self.page_size)))
        
        try:
            page = int(req.args[self.argument])
        except (KeyError, ValueError):
            page = 1
        if page < 1:
            page = page_count + page
        page = max(1, page)
        page = min(page_count, page)
        
        offset = self.page_size * (page - 1)
        query = query[offset:offset+self.page_size]
        
        return PaginatorResults(req, self, page_count, page, query)
        
class PaginatorResults(object):
    def __init__(self, req, paginator, page_count, page, query):
        self.req = req
        self.paginator = paginator
        self.page_count = page_count
        self.page = page
        self.query = query
        
        for method in ['all', 'one', 'first', 'count']:
            setattr(self, method, getattr(query, method))
        
        self.path = req.environ.get('SCRIPT_NAME', '').rstrip('/') + '/' + \
                    req.environ['PATH_INFO'].lstrip('/')
        self.args = []
        for key, vals in req.args.lists():
            if key == paginator.argument:
                continue
            for val in vals:
                self.args.append((key, val))
        
    def page_url(self, page_num):
        args = self.args[:]
        args.append((self.paginator.argument, unicode(page_num)))
        encoded_args = self.req.urlencode(args)
        return self.path + '?' + encoded_args
        
    def __iter__(self):
        return self.query.__iter__()