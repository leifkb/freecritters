# -*- coding: utf-8 -*-

from sqlalchemy import DynamicMetaData, Table, Column, Integer, Unicode, \
                       mapper, Binary, DateTime, func, ForeignKey, relation, \
                       backref, UniqueConstraint, Index, object_session, and_
from sqlalchemy.sql import literal
import sha
import re
from random import randint
from struct import pack
from datetime import datetime, timedelta
try:
    import uuid
except ImportError:
    from freecritters import _uuid as uuid
    
metadata = DynamicMetaData()

users = Table('users', metadata,
    Column('user_id', Integer, primary_key=True, nullable=False),
    Column('username', Unicode, nullable=False),
    Column('unformatted_username', Unicode, unique=True, index=True,
           nullable=False),
    Column('password', Binary(20), nullable=False),
    Column('salt', Binary(4), nullable=False),
    Column('profile', Unicode, nullable=False),
    Column('money', Integer, nullable=False),
    Column('registration_date', DateTime, nullable=False)
)

class PasswordHolder(object):
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
        
class User(PasswordHolder):
    username_length = 20
    # Now I have two problems.
    username_regex = re.compile(ur'^(?=.{1,%s}$)[ _-]*[A-Za-z][A-Za-z0-9 _-]*$' % username_length)
    
    def __init__(self, username, password, money=0):
        """Password should be unhashed."""
        
        super(User, self).__init__()
        self.change_username(username)
        self.change_password(password)
        self.money = money
        self.registration_date = datetime.utcnow()
    
    _unformat_username_regex = re.compile(ur'[^a-zA-Z0-9]+')
    @classmethod
    def unformat_username(self, username):
        """Removes formatting from a username."""
        
        username = self._unformat_username_regex.sub(u'', username)
        username = username.lower()
        return username
        
    def change_username(self, username):
        """Changes the username. Also changes the unformatted username and
        validates the new username.
        """
        
        if self.username_regex.search(username) is None:
            raise ValueError("Invalid username.")
        self.username = username
        self.unformatted_username = self.unformat_username(username)
        
    @classmethod
    def find_user(cls, sess, username):
        """Finds a user by username or (stringified) user ID. Returns None if
        the user doesn't exist.
        """
        if username.isdigit():
            return sess.query(cls).get(int(username))
        else:
            username = cls.unformat_username(username)
            return sess.query(cls).get_by_unformatted_username(username)
            
user_mapper = mapper(User, users)

subaccounts = Table('subaccounts', metadata,
    Column('subaccount_id', Integer, primary_key=True, nullable=False),
    Column('user_id', Integer, ForeignKey('users.user_id'), index=True,
           nullable=False),
    Column('name', Unicode, primary_key=True, nullable=False),
    Column('password', Binary(20), nullable=False),
    Column('salt', Binary(4), nullable=False),
    UniqueConstraint('user_id', 'name')
)

Index('idx_subaccounts_userid_name', subaccounts.c.user_id, subaccounts.c.name)

class Subaccount(PasswordHolder):
    def __init__(self, user, name, password):
        super(Subaccount, self).__init__()
        self.user = user
        self.name = name
        self.change_password(password)

subaccount_mapper = mapper(Subaccount, subaccounts, properties={
    'user': relation(User, backref=backref('subaccounts',
                                           cascade='all, delete-orphan'))
})

logins = Table('logins', metadata,
    Column('login_id', Integer, primary_key=True, nullable=False),
    Column('code', Unicode, nullable=False),
    Column('creation_time', DateTime, nullable=False),
    Column('user_id', Integer, ForeignKey('users.user_id'), index=True,
           nullable=False),
    Column('subaccount_id', Integer, ForeignKey('subaccounts.subaccount_id'),
           index=True)
)

class Login(object):
    def __init__(self, user, subaccount=None):
        self.user = user
        self.subaccount = subaccount
        self.code = unicode(uuid.uuid4())
        self.creation_time = datetime.utcnow()
    
    def form_token(self):
        return self.form_token_object().token
    
    def form_token_object(self):
        sess = object_session(self)
        return FormToken.form_token_for(sess, self.user, self.subaccount)

login_mapper = mapper(Login, logins, properties={
    'user': relation(User, backref=backref('logins',
                                           cascade='all, delete-orphan')),
    'subaccount': relation(Subaccount, backref=backref('logins'))
})

form_tokens = Table('form_tokens', metadata,
    Column('form_token_id', Integer, primary_key=True, nullable=False),
    Column('token', Unicode, nullable=False),
    Column('creation_time', DateTime, index=True, nullable=False),
    Column('user_id', Integer, ForeignKey('users.user_id'), nullable=False),
    Column('subaccount_id', Integer, ForeignKey('subaccounts.subaccount_id'),
           index=True)
)
Index('idx_formtokens_userid_subaccountid_creationtime_token',
      form_tokens.c.user_id, form_tokens.c.subaccount_id,
      form_tokens.c.creation_time, form_tokens.c.token)

class FormToken(object):
    def __init__(self, user, subaccount=None):
        self.user = user
        self.subaccount = subaccount
        self.token = unicode(uuid.uuid4())
        self.creation_time = datetime.utcnow()
    
    @classmethod
    def form_token_for(cls, sess, user, subaccount=None):
        """Finds or creates a form token for a user and subaccount and returns
        it. If a token is created, it will be automatically saved in the
        session.
        """
        
        query = sess.query(cls)
        min_creation_time = datetime.utcnow() - timedelta(days=1)
        if subaccount is None:
            subaccount_clause = cls.c.subaccount_id==None
        else:
            subaccount_clause = cls.c.subaccount_id==subaccount.subaccount_id
        clause = and_(
            cls.c.user_id==user.user_id,
            subaccount_clause,
            cls.c.creation_time>=min_creation_time)
        form_token = query.selectfirst(clause)
        if form_token is None:
            form_token = cls(user, subaccount)
            sess.save(form_token)
        return form_token
    
    @classmethod
    def find_form_token(cls, sess, token, user, subaccount=None):
        """Finds an existing form token, or returns None if it doesn't
        exist.
        """
        
        # Blah, blah, reuse code instead of copying and pasting, blah blah...
        query = sess.query(cls)
        min_creation_time = datetime.utcnow() - timedelta(days=7)
        if subaccount is None:
            subaccount_clause = cls.c.subaccount_id==None
        else:
            subaccount_clause = cls.c.subaccount_id==subaccount.subaccount_id
        clause = and_(
            cls.c.user_id==user.user_id,
            subaccount_clause,
            cls.c.creation_time>=min_creation_time,
            cls.c.token==token)
        form_token = query.selectfirst(clause)
        return form_token
        
form_token_mapper = mapper(FormToken, form_tokens, properties={
    'user': relation(User, backref=backref('form_tokens',
                                           cascade='all, delete-orphan')),
    'subaccount': relation(Subaccount, backref=backref('form_tokens'))
})
