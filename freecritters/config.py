# -*- coding: utf-8 -*-

from storm.locals import create_database
import yaml
import os.path

class ConfigurationError(Exception):
    pass

class Configuration(object):
    """freeCritters configuration."""
    
    def __init__(self, d):
        self.__dict__ = d

    def __repr__(self):
        return 'Configuration(%r)' % self.__dict__

def _process(value):
    if isinstance(value, str):
        return value.decode('utf8')
    elif isinstance(value, dict):
        d = value
        for key, value in d.iteritems():
            d[key] = _process(value)
        return Configuration(d)
    elif isinstance(value, list):
        return [_process(item) for item in value]
    else:
        return value

def _merge(defaults, config):
    result = dict(defaults)
    
    for key, value in config.iteritems():
        if key in result and isinstance(value, dict) \
           and isinstance(result[key], dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = value
            
    return _process(result)

def _load_yaml_dict(filename):
    try:
        text = open(filename).read()
    except IOError:
        raise ConfigurationError('Failed to read configuration file %s.' % filename)
    data = yaml.safe_load(text)
    if data is None:
        return {}
    elif isinstance(data, dict):
        return data
    else:
        raise ConfigurationError('Configuration file %s: wanted dict, got %s' % type(data).__name__)
    
_default_filename = os.path.join(os.path.dirname(__file__), 'defaults.yaml')
_default_dict = _load_yaml_dict(_default_filename)

def config_from_dict(d):
    config = _merge(_default_dict, d)
    config.database.db = create_database(config.database.url)
    if config.database.echo:
        from storm import database
        database.DEBUG = True
    return config

def config_from_yaml(filename):
    return config_from_dict(_load_yaml_dict(filename))