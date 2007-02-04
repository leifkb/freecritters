# -*- coding: utf-8 -*-

from sqlalchemy import DynamicMetaData, Table, Column, Integer, Unicode, \
                       mapper, Binary, DateTime, func, ForeignKey, relation, \
                       backref, UniqueConstraint, Index, object_session, \
                       and_, Boolean, select, func, cast
from sqlalchemy.sql import literal
import sha
import re
from random import randint
from struct import pack
from datetime import datetime, timedelta
from freecritters.textformats import plain_text
try:
    import uuid
except ImportError:
    from freecritters import _uuid as uuid

def _foreign_key(name):
    """Shortcut for a cascaded foreign key."""
    
    return ForeignKey(name, onupdate='CASCADE', ondelete='CASCADE')

metadata = DynamicMetaData()

users = Table('users', metadata,
    Column('user_id', Integer, primary_key=True, nullable=False),
    Column('username', Unicode, nullable=False),
    Column('unformatted_username', Unicode, unique=True, index=True,
           nullable=False),
    Column('password', Binary(20), nullable=False),
    Column('salt', Binary(4), nullable=False),
    Column('profile', Unicode, nullable=False),
    Column('profile_format', Unicode(32), nullable=False),
    Column('rendered_profile', Unicode, nullable=False),
    Column('default_format', Unicode(32), nullable=False),
    Column('money', Integer, nullable=False),
    Column('registration_date', DateTime(timezone=False), nullable=False),
    Column('pre_mail_message', Unicode(512)),
    Column('last_inbox_view', DateTime(timezone=False))
)

subaccounts = Table('subaccounts', metadata,
    Column('subaccount_id', Integer, primary_key=True, nullable=False),
    Column('user_id', Integer, ForeignKey('users.user_id'), index=True,
           nullable=False),
    Column('name', Unicode, nullable=False),
    Column('password', Binary(20), nullable=False),
    Column('salt', Binary(4), nullable=False),
    UniqueConstraint('user_id', 'name')
)
Index('idx_subaccounts_userid_name', subaccounts.c.user_id, subaccounts.c.name)

logins = Table('logins', metadata,
    Column('login_id', Integer, primary_key=True, nullable=False),
    Column('code', Unicode, nullable=False),
    Column('creation_time', DateTime(timezone=False), nullable=False),
    Column('user_id', Integer, _foreign_key('users.user_id'), index=True,
           nullable=False),
    Column('subaccount_id', Integer,
           _foreign_key('subaccounts.subaccount_id'), index=True)
)

form_tokens = Table('form_tokens', metadata,
    Column('form_token_id', Integer, primary_key=True, nullable=False),
    Column('token', Unicode, nullable=False),
    Column('creation_time', DateTime(timezone=False), index=True, nullable=False),
    Column('user_id', Integer, _foreign_key('users.user_id'), nullable=False),
    Column('subaccount_id', Integer,
           _foreign_key('subaccounts.subaccount_id'), index=True)
)
Index('idx_formtokens_userid_subaccountid_creationtime_token',
      form_tokens.c.user_id, form_tokens.c.subaccount_id,
      form_tokens.c.creation_time, form_tokens.c.token)

mail_conversations = Table('mail_conversations', metadata,
    Column('conversation_id', Integer, primary_key=True, nullable=False),
    Column('subject', Unicode(128), nullable=False),
    Column('creation_time', DateTime(timezone=False), nullable=False)
)

mail_participants = Table('mail_participants', metadata,
    Column('participant_id', Integer, primary_key=True, nullable=False),
    Column('conversation_id', Integer,
           _foreign_key('mail_conversations.conversation_id'),
           index=True, nullable=False),
    Column('user_id', Integer, _foreign_key('users.user_id')),
    Column('last_change', DateTime(timezone=False), nullable=False),
    Column('last_view', DateTime(timezone=False)),
    Column('deleted', Boolean, nullable=False),
    Column('system', Boolean, nullable=False),
    UniqueConstraint('conversation_id', 'user_id')
)
Index('idx_mailparticipants_userid_deleted_lastchange',
      mail_participants.c.user_id, mail_participants.c.deleted,
      mail_participants.c.last_change
)
Index('idx_mailparticipants_userid_deleted_system_lastchange',
      mail_participants.c.user_id, mail_participants.c.deleted,
      mail_participants.c.system, mail_participants.c.last_change
)

mail_messages = Table('mail_messages', metadata,
    Column('message_id', Integer, primary_key=True, nullable=False),
    Column('conversation_id', Integer,
           _foreign_key('mail_conversations.conversation_id'), index=True,
           nullable=False),
    Column('user_id', Integer, _foreign_key('users.user_id'), nullable=False),
    Column('message', Unicode, nullable=False),
    Column('message_format', Unicode(32), nullable=False),
    Column('rendered_message', Unicode, nullable=False),
    Column('sent', DateTime(timezone=False), nullable=False)
)
Index('idx_mailmessages_conversationid_sent',
      mail_messages.c.conversation_id,
      mail_messages.c.sent
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
    username_regex = re.compile(
        ur'^(?=.{1,%s}$)[ _-]*[A-Za-z][A-Za-z0-9 _-]*$' % username_length)
    pre_mail_message_max_length = 300
    
    def __init__(self, username, password, money=0):
        """Password should be unhashed."""
        
        super(User, self).__init__()
        self.change_username(username)
        self.change_password(password)
        self.money = money
        self.registration_date = datetime.utcnow()
        self.profile = u''
        self.rendered_profile = u''
        self.profile_format = u'html_auto'
        self.default_format = u'html_auto'
        self.pre_mail_message = None
        self.last_inbox_view = None
        
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
        
    def render_pre_mail_message(self):
        if self.pre_mail_message is None:
            return None
        else:
            return plain_text(self.pre_mail_message, 3)
        
    def has_new_mail(self):
        conn = object_session(self).connection(MailParticipant)
        query = select([func.max(mail_participants.c.last_change)],
                       and_(mail_participants.c.user_id==self.user_id,
                            mail_participants.c.deleted==False))
        last_mail_change = conn.execute(query).fetchone()[0]
        if last_mail_change is None:
            return False
        else:
            return self.last_inbox_view is None \
                or self.last_inbox_view < last_mail_change
            
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
            
class Subaccount(PasswordHolder):
    def __init__(self, user, name, password):
        super(Subaccount, self).__init__()
        self.user = user
        self.name = name
        self.change_password(password)

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

class MailConversation(object):
    max_subject_length = 64
    
    def __init__(self, subject):
        self.subject = subject
        self.creation_time = datetime.utcnow()
    
    def can_be_viewed_by(self, user, subaccount):
        for participant in self.participants:
            if participant.deleted == False and participant.user == user:
                return True
        else:
            return False
    
    def can_be_replied_to_by(self, user, subaccount):
        return self.can_be_viewed_by(user, subaccount)
        
class MailParticipant(object):
    def __init__(self, conversation, user, system=False):
        self.conversation = conversation
        self.user = user
        self.last_change = datetime.utcnow()
        self.last_view = None
        self.deleted = False
        self.system = system

    @classmethod
    def where_clause(cls, user, user2=None, system=None):
        result = and_(
            mail_participants.c.user_id==user.user_id,
            mail_participants.c.deleted==False
        )
        if system is not None:
            result = and_(result, mail_participants.c.system==system)
        if user2 is not None:
            mp2 = mail_participants.alias('mail_participants2')
            result = and_(
                result,
                mp2.c.conversation_id==mail_participants.c.conversation_id,
                mp2.c.user_id==user2.user_id
            )
        return result
        
class MailMessage(object):
    def __init__(self, conversation, user, message, message_format,
                 rendered_message):
        self.conversation = conversation
        self.user = user
        self.message = message
        self.message_format = message_format
        self.rendered_message = rendered_message
        self.sent = datetime.utcnow()
        
login_mapper = mapper(Login, logins, properties={
    'user': relation(User, backref=backref('logins',
                                           cascade='all, delete-orphan')),
    'subaccount': relation(Subaccount, backref=backref('logins'))
})
        
form_token_mapper = mapper(FormToken, form_tokens, properties={
    'user': relation(User, backref=backref('form_tokens',
                                           cascade='all, delete-orphan')),
    'subaccount': relation(Subaccount, backref=backref('form_tokens'))
})

user_mapper = mapper(User, users)

subaccount_mapper = mapper(Subaccount, subaccounts, properties={
    'user': relation(User, backref=backref('subaccounts',
                                           cascade='all, delete-orphan'))
})

mail_conversation_mapper = mapper(MailConversation, mail_conversations)

mail_participant_mapper = mapper(MailParticipant, mail_participants, properties={
    'conversation': relation(MailConversation, lazy=False,
                             backref=backref('participants',
                                             cascade='all, delete-orphan')),
    'user': relation(User, lazy=False,
                     backref=backref('participations',
                                     cascade='all, delete-orphan'))
})

mail_message_mapper = mapper(MailMessage, mail_messages, properties={
    'conversation': relation(MailConversation,
                             backref=backref('messages',
                                             cascade='all, delete-orphan',
                                             order_by=mail_messages.c.sent)),
    'user': relation(User, backref=backref('messages',
                                           cascade='all, delete-orphan'))
})
