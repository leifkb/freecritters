# -*- coding: utf-8 -*-

from sqlalchemy import DynamicMetaData, Table, Column, Integer, Unicode, \
                       mapper, Binary, DateTime, func, ForeignKey, relation, \
                       backref, UniqueConstraint, Index, object_session, \
                       and_, Boolean, select, func, cast, String, \
                       create_session, Query, deferred
from sqlalchemy.sql import literal
from sqlalchemy.ext.sessioncontext import SessionContext
from sqlalchemy.orm.mapper import global_extensions
import sha
import re
from random import randint
from struct import pack
from datetime import datetime, timedelta
from freecritters.textformats import render_plain_text
try:
    import uuid
except ImportError:
    from freecritters import _uuid as uuid
import Image
from cStringIO import StringIO

def _foreign_key(name):
    """Shortcut for a cascaded foreign key."""
    
    return ForeignKey(name, onupdate='CASCADE', ondelete='CASCADE')

ctx = SessionContext(create_session)
global_extensions.append(ctx.mapper_extension)

metadata = DynamicMetaData()

users = Table('users', metadata,
    Column('user_id', Integer, primary_key=True, nullable=False),
    Column('username', Unicode, nullable=False),
    Column('unformatted_username', Unicode, unique=True, index=True,
           nullable=False),
    Column('password', Binary(20), nullable=False),
    Column('salt', Binary(4), nullable=False),
    Column('profile', Unicode, nullable=False),
    Column('rendered_profile', Unicode, nullable=False),
    Column('money', Integer, nullable=False),
    Column('registration_date', DateTime(timezone=False), nullable=False),
    Column('pre_mail_message', Unicode(512)),
    Column('last_inbox_view', DateTime(timezone=False)),
    Column('role_id', Integer, ForeignKey('roles.role_id'), nullable=False)
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
    Column('rendered_message', Unicode, nullable=False),
    Column('sent', DateTime(timezone=False), nullable=False)
)
Index('idx_mailmessages_conversationid_sent',
      mail_messages.c.conversation_id,
      mail_messages.c.sent
)

permissions = Table('permissions', metadata,
    Column('permission_id', Integer, primary_key=True, nullable=False),
    Column('label', Unicode(32), unique=True, nullable=True),
    Column('title', Unicode(128), nullable=False),
    Column('description', Unicode, nullable=False)
)

roles = Table('roles', metadata,
    Column('role_id', Integer, primary_key=True, nullable=False),
    Column('label', Unicode(32), unique=True, nullable=True),
    Column('name', Unicode(128), nullable=False)
)

role_permissions = Table('role_permissions', metadata,
    Column('role_id', Integer, _foreign_key('roles.role_id'),
           primary_key=True),
    Column('permission_id', Integer, _foreign_key('permissions.permission_id'),
           primary_key=True)
)

subaccount_permissions = Table('subaccount_permissions', metadata,
    Column('subaccount_id', Integer, _foreign_key('subaccounts.subaccount_id'),
           primary_key=True),
    Column('permission_id', Integer, _foreign_key('permissions.permission_id'),
           primary_key=True)
)

#forums = Table('forums', metadata,
#    Column('forum_id', Integer, primary_key=True),

pictures = Table('pictures', metadata,
    Column('picture_id', Integer, primary_key=True),
    Column('added', DateTime(timezone=False), nullable=False),
    Column('name', Unicode(128), nullable=False),
    Column('copyright', Unicode, nullable=False),
    Column('description', Unicode, nullable=False),
    Column('width', Integer, nullable=False),
    Column('height', Integer, nullable=False),
    Column('format', String(16), nullable=False),
    Column('image', Binary, nullable=False)
)

resized_pictures = Table('resized_pictures', metadata,
    Column('resized_picture_id', Integer, primary_key=True),
    Column('picture_id', Integer, _foreign_key('pictures.picture_id'), index=True, nullable=False),
    Column('added', DateTime(timezone=False), nullable=False),
    Column('last_used', DateTime(timezone=False), index=True),
    Column('width', Integer, nullable=False),
    Column('height', Integer, nullable=False),
    Column('image', Binary, nullable=False)
)
Index('idx_resizedpictures_pictureid_width_height',
    resized_pictures.c.picture_id,
    resized_pictures.c.width,
    resized_pictures.c.height
)

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
        
class User(PasswordHolder):
    username_length = 20
    username_regex = re.compile( # Now I have two problems
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
        validates the new username (ValueError is raised if it's invalid).
        """
        
        if self.username_regex.search(username) is None:
            raise ValueError("Invalid username.")
        self.username = username
        self.unformatted_username = self.unformat_username(username)
        
    def render_pre_mail_message(self):
        if self.pre_mail_message is None:
            return None
        else:
            return render_plain_text(self.pre_mail_message, 3)
        
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
    def find_user(cls, username):
        """Finds a user by username or (stringified) user ID. Returns None if
        the user doesn't exist.
        """
        if username.isdigit():
            return Query(cls).get(int(username))
        else:
            username = cls.unformat_username(username)
            return Query(cls).get_by_unformatted_username(username)
            
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

class FormToken(object):
    def __init__(self, user, subaccount=None):
        self.user = user
        self.subaccount = subaccount
        self.token = unicode(uuid.uuid4())
        self.creation_time = datetime.utcnow()
    
    @classmethod
    def form_token_for(cls, user, subaccount=None):
        """Finds or creates a form token for a user and subaccount and returns
        it. If a token is created, it will be automatically saved in the
        database session.
        """
        
        query = Query(cls)
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
        return form_token
    
    @classmethod
    def find_form_token(cls, token, user, subaccount=None):
        """Finds an existing form token, or returns None if it doesn't
        exist.
        """
        # Blah, blah, reuse code instead of copying and pasting, blah blah...
        query = Query(cls)
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
    max_subject_length = 45
    
    def __init__(self, subject):
        self.subject = subject
        self.creation_time = datetime.utcnow()
    
    def find_participant(self, user):
        for participant in self.participants:
            if participant.user == user and participant.deleted == False:
                return participant
        return None
        
    def can_be_viewed_by(self, user, subaccount):
        return self.find_participant(user) is not None
    
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

    def delete(self):
        self.deleted = True
        for participant in self.conversation.participants:
            if not participant.deleted:
                break
        else:
            object_session(self).delete(self.conversation)
        
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
    def __init__(self, conversation, user, message, rendered_message):
        self.conversation = conversation
        self.user = user
        self.message = message
        self.rendered_message = rendered_message
        self.sent = datetime.utcnow()
        
class Permission(object):
    def __init__(self, title, description, label=None):
        self.title = title
        self.description = description
        self.label = label
        
    @classmethod
    def find_label(cls, label, allow_none=False):
        result = Query(cls).get_by_label(label)
        if not allow_none:
            assert result is not None, \
                'Permission labelled %r not found.' % label
        return result
    
    def possessed_by(self, user, subaccount=None):
        """Checks whether this permission is possessed by a given user and,
        optionally, subaccount.
        """
        
        result = self in user.role.permissions
                
        if result and subaccount is not None:
            result = self in subaccount.permissions
        
        return result
        
class Role(object):
    def __init__(self, name, label=None):
        self.label = label
        self.name = name
    
    @classmethod
    def find_label(cls, label, allow_none=False): # Whee! Duplication!
        result = Query(cls).get_by_label(label)
        if not allow_none:
            assert result is not None, 'Role labelled %r not found.' % label
        return result
    
class Picture(object):
    def __init__(self, name, copyright, description, image):
        self.name = name
        self.copyright = copyright
        self.description = description
        self.change_image(image)
        self.added = datetime.utcnow()        
    
    def change_image(self, image):
        """Changes the image. Argument can be a PIL image, a file-like object
        containing image data, or a byte string containing image data."""
        if isinstance(image, Image.Image):
            pil_image = image
            image = None
        elif isinstance(image, str):
            pil_image = Image.open(StringIO(image))
        else:
            image = image.read()
            pil_image = Image.open(StringIO(image))
        format = pil_image.format
        if format not in ('PNG', 'JPEG'):
            image = None
            format = 'PNG'
        if image is None:
            image = StringIO()
            pil_image.save(image, format)
            image = image.getvalue()
        self.width, self.height = pil_image.size
        self.format = format
        self.image = image
    
    _mime_types = {
        'PNG': 'image/png',
        'JPEG': 'image/jpeg'
    }
    
    @property
    def mime_type(self):
        try:
            return self._mime_types[self.format]
        except KeyError:
            raise AssertionError("Unknown format %r." % self.format)
    
    _extensions = {
        'PNG': '.png',
        'JPEG': '.jpeg'
    }
    
    @property
    def extension(self):
        try:
            return self._extensions[self.format]
        except KeyError:
            raise AssertionError("Unknown format %r." % self.format)
    
    @property
    def pil_image(self):
        data = StringIO(self.image)
        return Image.open(data)
    
    def resized_within(self, width, height):
        """Like resized_to, but the resulting image will fit within the
        dimensions while preserving its aspect ration.
        """
        if width > self.width and height > self.height:
            return self
        if self.width > width:
            new_height = int(round(max(self.height * width / float(self.width), 1.0)))
            new_width = width
        else:
            new_width = int(round(max(self.width * height / float(self.height), 1.0)))
            new_height = height
        return self.resized_to(new_width, new_height)
    
    def resized_to(self, width, height):
        """Resizes the picture to the given dimensions. Returns a ResizedPicture,
        or self if the dimensions are the same.
        """
        if width == self.width and height == self.height:
            return self
        picture = Query(ResizedPicture).get_by(picture_id=self.picture_id,
                                               width=width, height=height)
        if picture is not None:
            return picture
        picture = ResizedPicture(self, width, height)
        ctx.current.flush()
        return picture

class ResizedPicture(object):
    def __init__(self, picture, width, height):
        self.picture = picture
        pil_image = picture.pil_image
            
        if pil_image.mode not in ('RGB', 'RGBA'):
            # Unfortunately, PIL doesn't support generating a palette from an
            # RGBA image, so we can't resize paletted images back into paletted
            # images.
            pil_image = pil_image.convert('RGBA')
            
        pil_image = pil_image.resize((width, height), Image.ANTIALIAS)

        image = StringIO()
        pil_image.save(image, picture.format)
        
        self.image = image.getvalue()
        self.added = datetime.utcnow()
        self.width = width
        self.height = height
        
    @property
    def pil_image(self):
        data = StringIO(self.image)
        return Image.open(data)
        
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

user_mapper = mapper(User, users, properties={
    'role': relation(Role, backref=backref('users'))
})

subaccount_mapper = mapper(Subaccount, subaccounts, properties={
    'user': relation(User, backref=backref('subaccounts',
                                           cascade='all, delete-orphan'))
})

mail_conversation_mapper = mapper(MailConversation, mail_conversations)

mail_participant_mapper = mapper(MailParticipant, mail_participants, properties={
    'conversation': relation(MailConversation, lazy=False,
                             backref=backref('participants', lazy=False,
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

permission_mapper = mapper(Permission, permissions, properties={
    'roles': relation(Role, secondary=role_permissions,
                      backref=backref('permissions',
                                      order_by=permissions.c.title)),
    'subaccounts': relation(Subaccount, secondary=subaccount_permissions,
                            backref='permissions')
})

picture_mapper = mapper(Picture, pictures, properties={
    'image': deferred(pictures.c.image)
})

resized_picture_mapper = mapper(ResizedPicture, resized_pictures, properties={
    'picture': relation(Picture, backref=backref('resized_pictures', cascade='all, delete-orphan')),
    'image': deferred(resized_pictures.c.image)
})

role_mapper = mapper(Role, roles)
