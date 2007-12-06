# -*- coding: utf-8 -*-

from freecritters.web.util import absolute_url
from datetime import datetime
from werkzeug.utils import get_current_url
from urlparse import urljoin
from os import path
from mako.lookup import TemplateLookup

loader = TemplateLookup([path.join(path.dirname(__file__), 'templates')],
                        imports=['from freecritters.web.globals import fc',
                                 'from freecritters.web.tabs import Tab',
                                 'from freecritters.web.filters import rss_time, integer, datetime'],
                        default_filters=['unicode', 'h'],
                        input_encoding='utf-8', output_encoding='utf-8')