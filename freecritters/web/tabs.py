# -*- coding: utf-8 -*-

class Tabs(object):
    def __init__(self, *tabs):
        self._tabs = []
        self._identity_map = {}
        for tab in tabs:
            self.add_tab(tab)
    
    def add_tab(self, tab):
        if tab.identity in self._identity_map:
            raise ValueError("Tab identity %r already present." % tab.identity)
        self._tabs.append(tab)
        self._identity_map[tab.identity] = tab
    
    def __iter__(self):
        for tab in self._tabs:
            yield tab 

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