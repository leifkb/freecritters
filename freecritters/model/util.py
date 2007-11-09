from sqlalchemy import and_
from sqlalchemy.orm import MapperExtension

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

class FieldCopierExtension(MapperExtension):
    def __init__(self, columns=None, **kwargs):
        if columns is not None:
            kwargs.update(columns)
        self.columns = kwargs

    def after_insert(self, mapper, connection, instance):
        clause = and_(*[
            col==value
            for col, value
            in zip(mapper.primary_key, mapper.primary_key_from_instance(instance))
        ])
        values = {}
        for col1, cols in self.columns.iteritems():
            if getattr(instance, col1) is None:
                value = getattr(instance, col2)
                setattr(instance, col1, value)
                values[col1] = col2
        if values:
            connection.execute(mapper.mapped_table.update(clause, values=values))
        return EXT_PASS