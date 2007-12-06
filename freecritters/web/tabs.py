# -*- coding: utf-8 -*-

class Tab(object):
    def __init__(self, text, endpoint, args=None, identity=None, **kwargs):
        if args is not None:
            kwargs.update(args)
        if identity is None:
            identity = endpoint
        self.identity = identity
        self.text = text
        self.endpoint = endpoint
        self.args = kwargs