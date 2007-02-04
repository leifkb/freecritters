# -*- coding: utf-8 -*-

from math import ceil
from urllib import urlencode

def _urlencode_utf8(args):
    return urlencode([(key, val.encode('utf8')) for key, val in args])

class Paginator(object):
    def __init__(self, req, items, page_size=25, query_argument='page'):
        self.page_size = self.limit = page_size
        self.num_pages = max(1, int(ceil(float(items) / page_size)))
        self.page_box_maxlength = len(str(self.num_pages))
        self.page_box_size = self.page_box_maxlength + 1
        self.query_argument = query_argument
        
        if query_argument in req.args:
            if req.args[query_argument] == '_':
                page_num = self.num_pages
            else:
                try:
                    page_num = int(req.args[query_argument])
                except ValueError:
                    page_num = 1
        else:
            page_num = 1
        self.page_num = min(self.num_pages, max(1, page_num))
        
        self.offset = self.page_size * (self.page_num - 1)
        self.kwargs = {'limit': self.limit, 'offset': self.offset}
        
        args = []
        for key, vals in req.args.lists():
            if key == query_argument:
                continue
            for val in vals:
                args.append((key, val))
        url = req.environ['APPLICATION_REQUEST']
        
        self.args = args
        
        if self.page_num > 1:
            self.prev_page_link = '%s?%s' % (url, _urlencode_utf8(args +
                [(query_argument, unicode(self.page_num - 1))]))
            self.first_page_link = '%s?%s' % (url, _urlencode_utf8(args +
                [(query_argument, u'1')]))
        else:
            self.prev_page_link = None
            self.first_page_link = None
        
        if self.page_num < self.num_pages:
            self.next_page_link = '%s?%s' % (url, _urlencode_utf8(args +
                [(query_argument, unicode(self.page_num + 1))]))
            self.last_page_link = '%s?%s' % (url, _urlencode_utf8(args +
                [(query_argument, unicode(self.num_pages))]))
        else:
            self.next_page_link = None
            self.last_page_link = None
