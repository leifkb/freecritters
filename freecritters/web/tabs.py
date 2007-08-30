# -*- coding: utf-8 -*-

class Tabs(object):
    def __init__(self, tabs):
        self.tabs = tabs
        self.active = None
    
    def activate(self, url):
        self.active = url