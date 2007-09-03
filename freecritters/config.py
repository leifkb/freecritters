# -*- coding: utf-8 -*-

from storm.locals import create_database
import yaml

class Configuration(object):
    """freeCritters configuration."""
    
    def __init__(self, db_url, site_name,
                       http_hostname='localhost', http_port=8080,
                       db_echo=False):
        self.db_url = db_url
        self.site_name = site_name
        self.db = create_database(db_url)
        if db_echo:
            from storm import database
            database.DEBUG = True
        self.http_hostname = http_hostname
        self.http_port = http_port
    
    @classmethod
    def read_dictionary(cls, dictionary):
        db_url = dictionary['db url']
        db_echo = dictionary.get('db echo', False)
        site_name = dictionary['site name'].decode('utf8')
        http_hostname = dictionary.get('http hostname', 'localhost')
        http_port = dictionary.get('http port', 8080)
        return cls(db_url, site_name, http_hostname, http_port, db_echo)
        
    @classmethod
    def read_yaml(cls, data):
        return cls.read_dictionary(yaml.load(data))
    
    @classmethod
    def read_yaml_file(cls, f):
        if isinstance(f, basestring):
            f = open(f)
        return cls.read_yaml(f.read())
