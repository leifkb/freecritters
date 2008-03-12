from sqlalchemy import and_
from sqlalchemy.orm import MapperExtension, EXT_CONTINUE, class_mapper, Query
from struct import pack
from random import randint
import sha

class PasswordHolder(object):
    """Helper class that can be subclassed to gain methods for dealing with a
    password.
    """
    
    def __init__(self):
        self.salt = pack('BBBB', *[randint(0, 255) for _ in xrange(4)])

    def hash_password(self, password):
        """Hashes and salts a password."""
        
        return sha.new(self.salt + password.encode('utf8')).digest()
    
    def change_password(self, password):
        """Changes the password. Password should be unhashed."""
        
        self.password = self.hash_password(password)
        
    def check_password(self, password):
        """Checks if an unhashed password is correct."""
        
        return self.hash_password(password) == str(self.password)

def _primary_key_clause(mapper, instance):
    return and_(*[
        col==value
        for col, value
        in zip(mapper.primary_key, mapper.primary_key_from_instance(instance))
    ])

class FieldCopierExtension(MapperExtension):
    def __init__(self, columns=None, **kwargs):
        if columns is not None:
            kwargs.update(columns)
        self.columns = kwargs

    def after_insert(self, mapper, connection, instance):
        clause = _primary_key_clause(mapper, instance)
        values = {}
        for col1, cols in self.columns.iteritems():
            if getattr(instance, col1) is None:
                value = getattr(instance, col2)
                setattr(instance, col1, value)
                values[col1] = col2
        if values:
            connection.execute(mapper.mapped_table.update(clause, values=values))
        return EXT_CONTINUE

class CountKeeperExtension(MapperExtension):
    def __init__(self, relation, attr):
        self.relation = relation
        self.attr = attr
    
    def _add(self, connection, instance, value):
        obj = getattr(instance, self.relation)
        if obj is not None:
            current_value = getattr(obj, self.attr)
            new_value = current_value + value
            setattr(obj, self.attr, new_value)
            mapper = class_mapper(type(obj))
            clause = _primary_key_clause(mapper, instance)
            connection.execute(mapper.mapped_table.update(clause, values={self.attr: new_value}))
    
    def after_insert(self, mapper, connection, instance):
        self._add(connection, instance, +1)
        return EXT_CONTINUE
        
    def before_delete(self, mapper, connection, instance):
        self._add(connection, instance, -1)
        return EXT_CONTINUE

def maybe_get(query, identity):
    if identity is None:
        return None
    else:
        return query.get(identity)

Query.maybe_get = maybe_get

def set_dynamic_relation(relation, items):
    current = set(relation)
    items = set(items)
    removed = current - items
    added = items - current
    for item in removed:
        print '\n\n\n\n\n\n', relation.all(), item, item in relation, item in relation.all()
        relation.remove(item)
    for item in added:
        relation.append(item)