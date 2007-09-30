# -*- coding: utf-8 -*-

from storm.locals import *
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
from StringIO import StringIO
import threading

ctx = threading.local()

class Base(Storm):
    @classmethod
    def find(cls, *args, **kwargs):
        return ctx.store.find(cls, *args, **kwargs)
    
    @classmethod
    def get(cls, *args, **kwargs):
        return ctx.store.get(cls, *args, **kwargs)
    
    def save(self):
        return ctx.store.add(self)
    
    def delete(self):
        ctx.store.remove(self)

class PasswordHolder(Base):
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
    __storm_table__ = 'users'
    username_length = 20
    username_regex = re.compile( # Now I have two problems
        ur'^(?=.{1,%s}$)[ _-]*[A-Za-z][A-Za-z0-9 _-]*$' % username_length)
    pre_mail_message_max_length = 300
    
    user_id = Int(primary=True)
    username = Unicode()
    unformatted_username = Unicode()
    password = RawStr()
    salt = RawStr()
    profile = Unicode()
    rendered_profile = Unicode()
    money = Int()
    registration_date = DateTime()
    pre_mail_message = Unicode()
    last_inbox_view = DateTime()
    role_id = Int()
    role = Reference(role_id, 'Role.role_id')
    subaccounts = ReferenceSet(user_id, 'Subaccount.user_id')
    logins = ReferenceSet(user_id, 'Logins.user_id')
    form_tokens = ReferenceSet(user_id, 'FormToken.user_id')
    permissions = ReferenceSet(role_id,
                               'RolePermission.role_id',
                               'RolePermission.permission_id',
                               'Permission.permission_id')
    pets = ReferenceSet(user_id, 'Pet.user_id')
    group_memberships = ReferenceSet(user_id, 'GroupMember.user_id')
    groups = ReferenceSet(user_id,
                          'GroupMember.user_id',
                          'GroupMember.group_id',
                          'Group.group_id')
    owned_group = Reference(user_id, 'Group.owner_user_id')
    
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
        last_mail_change = Store.of(self).find(
            MailParticipant,
            MailParticipant.user_id==self.user_id,
            MailParticipant.deleted==False
        ).max(MailParticipant.last_change) 
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
            return cls.get(int(username))
        else:
            username = cls.unformat_username(username)
            return cls.find(User.unformatted_username==username).one()
    
    def find_group_memnership(self, group):
        return self.group_memberships.find(group_id==group.group_id).one()
        
class Subaccount(PasswordHolder):
    __storm_table__ = 'subaccounts'
    subaccount_id = Int(primary=True)
    user_id = Int()
    user = Reference(user_id, 'User.user_id')
    name = Unicode()
    password = RawStr()
    salt = RawStr()
    form_tokens = ReferenceSet(subaccount_id, 'FormToken.subaccount_id')
    permissions = ReferenceSet(subaccount_id,
                               'SubaccountPermission.subaccount_id',
                               'SubaccountPermission.permission_id',
                               'Permission.permission_id')
                               
    def __init__(self, user, name, password):
        super(Subaccount, self).__init__()
        self.user = user
        self.name = name
        self.change_password(password)

class Login(Base):
    __storm_table__ = 'logins'
    login_id = Int(primary=True)
    code = Unicode()
    creation_time = DateTime()
    user_id = Int()
    user = Reference(user_id, 'User.user_id')
    subaccount_id = Int()
    subaccount = Reference(subaccount_id, 'Subaccount.subaccount_id')
    
    def __init__(self, user, subaccount=None):
        self.user = user
        self.subaccount = subaccount
        self.code = unicode(uuid.uuid4())
        self.creation_time = datetime.utcnow()

class FormToken(Base):
    __storm_table__ = 'form_tokens'
    form_token_id = Int(primary=True)
    token = Unicode()
    creation_time = DateTime()
    user_id = Int()
    user = Reference(user_id, 'User.user_id')
    subaccount_id = Int()
    subaccount = Reference(subaccount_id, 'Subaccount.subaccount_id')
    
    def __init__(self, user, subaccount=None):
        self.user = user
        self.subaccount = subaccount
        self.token = unicode(uuid.uuid4())
        self.creation_time = datetime.utcnow()
    
    @classmethod
    def form_token_for(cls, user, subaccount=None):
        """Finds or creates a form token for a user and subaccount and returns
        it. If a token is created, it will be automatically saved in the
        database store.
        """
        
        min_creation_time = datetime.utcnow() - timedelta(days=1)
        if subaccount is None:
            subaccount_clause = cls.subaccount_id==None
        else:
            subaccount_clause = cls.subaccount_id==subaccount.subaccount_id
        form_token = cls.find(
            cls.user_id==user.user_id,
            subaccount_clause,
            cls.creation_time>=min_creation_time
        ).any()
        if form_token is None:
            form_token = cls(user, subaccount)
            form_token.save()
        return form_token
    
    @classmethod
    def find_form_token(cls, token, user, subaccount=None):
        """Finds an existing form token, or returns None if it doesn't
        exist.
        """
        # Blah, blah, reuse code instead of copying and pasting, blah blah...
        min_creation_time = datetime.utcnow() - timedelta(days=7)
        if subaccount is None:
            subaccount_clause = cls.subaccount_id==None
        else:
            subaccount_clause = cls.subaccount_id==subaccount.subaccount_id
        form_token = cls.find(
            cls.user_id==user.user_id,
            subaccount_clause,
            cls.creation_time>=min_creation_time,
            cls.token==token
        ).any()
        return form_token

class MailConversation(Base):
    max_subject_length = 45
    __storm_table__ = 'mail_conversations'
    conversation_id = Int(primary=True)
    subject = Unicode()
    creation_time = DateTime()
    participants = ReferenceSet(conversation_id, 'MailParticipant.conversation_id')
    messages = ReferenceSet(conversation_id, 'MailMessage.conversation_id')
    
    def __init__(self, subject):
        self.subject = subject
        self.creation_time = datetime.utcnow()
    
    def find_participant(self, user):
        return self.participants.find(
            MailParticipant.user_id==user.user_id,
            MailParticipant.deleted==False
        ).one()
        
    def can_be_viewed_by(self, user, subaccount):
        return self.find_participant(user) is not None
    
    def can_be_replied_to_by(self, user, subaccount):
        return self.can_be_viewed_by(user, subaccount)
        
class MailParticipant(Base):
    __storm_table__ = 'mail_participants'
    participant_id = Int(primary=True)
    conversation_id = Int()
    conversation = Reference(conversation_id, 'MailConversation.conversation_id')
    user_id = Int()
    user = Reference(user_id, 'User.user_id')
    last_change = DateTime()
    last_view = DateTime()
    deleted = Bool()
    system = Bool()
    
    def __init__(self, conversation, user, system=False):
        self.conversation = conversation
        self.user = user
        self.last_change = datetime.utcnow()
        self.last_view = None
        self.deleted = False
        self.system = system

    def delete(self):
        self.deleted = True
        non_deleted_count = MailParticipant.find(
            MailParticipant.conversation_id==self.conversation_id,
            MailParticipant.deleted==False
        ).count()
        if non_deleted_count == 0:
            self.conversation.delete()
        
    @classmethod
    def where_clause(cls, user, user2=None, system=None):
        result = And(
            MailParticipant.user_id==user.user_id,
            MailParticipant.deleted==False
        )
        if system is not None:
            result = And(result, MailParticipant.system==system)
        if user2 is not None:
            mp2 = ClassAlias(MailParticipant)
            result = And(
                result,
                mp2.conversation_id==MailParticipant.conversation_id,
                mp2.user_id==user2.user_id
            )
        return result
        
class MailMessage(Base):
    __storm_table__ = 'mail_messages'
    message_id = Int(primary=True)
    conversation_id = Int()
    conversation = Reference(conversation_id, 'MailConversation.conversation_id')
    user_id = Int()
    user = Reference(user_id, 'User.user_id')
    message = Unicode()
    rendered_message = Unicode()
    sent = DateTime()
    
    def __init__(self, conversation, user, message, rendered_message):
        self.conversation = conversation
        self.user = user
        self.message = message
        self.rendered_message = rendered_message
        self.sent = datetime.utcnow()
        
class Permission(Base):
    __storm_table__ = 'permissions'
    permission_id = Int(primary=True)
    label = Unicode()
    title = Unicode()
    description = Unicode()
    
    def __init__(self, title, description, label=None):
        self.title = title
        self.description = description
        self.label = label
        
    @classmethod
    def find_label(cls, label, allow_none=False):
        result = cls.find(label=label).one()
        if not allow_none:
            assert result is not None, \
                'Permission labelled %r not found.' % label
        return result
    
    def possessed_by(self, user, subaccount=None):
        """Checks whether this permission is possessed by a given user and,
        optionally, subaccount.
        """
        
        result = bool(user.role.permissions.find(
            Permission.permission_id==self.permission_id
        ).count())
        
        if result and subaccount is not None:
            result = bool(Subaccount.permissions.find(
                Permission.permission_id==self.permission_id
            ).count())
        
        return result
        
class Role(Base):
    __storm_table__ = 'roles'
    role_id = Int(primary=True)
    label = Unicode()
    name = Unicode()
    permissions = ReferenceSet(role_id,
                               'RolePermission.role_id',
                               'RolePermission.permission_id',
                               'Permission.permission_id')
                               
    def __init__(self, name, label=None):
        self.label = label
        self.name = name
    
    @classmethod
    def find_label(cls, label, allow_none=False): # Whee! Duplication!
        result = cls.find(label=label).one()
        if not allow_none:
            assert result is not None, 'Role labelled %r not found.' % label
        return result

class RolePermission(Base):
    __storm_table__ = 'role_permissions'
    __storm_primary__ = 'role_id', 'permission_id'
    role_id = Int()
    role = Reference(role_id, 'Role.role_id')
    permission_id = Int()
    permission = Reference(permission_id, 'Permission.permission_id')

class SubaccountPermission(Base):
    __storm_table__ = 'subaccount_permissions'
    __storm_primary__ = 'subaccount_id', 'permission_id'
    subaccount_id = Int()
    subaccount = Reference(subaccount_id, 'Subaccount.subaccount_id')
    permission_id = Int()
    permission = Reference(permission_id, 'Subaccount.subaccount_id')

class Picture(Base):
    __storm_table__ = 'pictures'
    picture_id = Int(primary=True)
    added = DateTime()
    name = Unicode()
    copyright = Unicode()
    description = Unicode()
    width = Int()
    height = Int()
    format = RawStr()
    image = RawStr()
    resized_images = ReferenceSet(picture_id, 'ResizedPictures.picture_id')
    
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
        picture = self.resized_pictures.find(width=width, height=height).any()
        if picture is not None:
            picture.last_used = datetime.utcnow()
            return picture
        picture = ResizedPicture(self, width, height)
        return picture

class ResizedPicture(Base):
    __storm_table__ = 'resized_pictures'
    resized_picture_id = Int(primary=True)
    picture_id = Int()
    picture = Reference(picture_id, 'Pictures.picture_id')
    added = DateTime()
    width = Int()
    height = Int()
    image = RawStr()
    
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

class Species(Base):
    __storm_table__ = 'species'
    species_id = Int(primary=True)
    name = Unicode()
    creatable = Bool()
    appearances = ReferenceSet(species_id,
                               'SpeciesAppearance.species_id',
                               'SpeciesAppearance.appearance_id',
                               'Appearance.appearance_id')
                           
    def __init__(self, name, creatable=True):
        self.name = name
        self.creatable = creatable
    
    @property
    def can_be_created(self):
        if not self.creatable:
            return False
        return bool(self.appearances.find(creatable=True).count())
    
    @classmethod
    def find_creatable(cls, *order_by):
        for obj in Species.find(creatable=True).order_by(*order_by):
            if obj.can_be_created:
                yield obj
        
class Appearance(Base):
    __storm_table__ = 'appearances'
    appearance_id = Int(primary=True)
    name = Unicode()
    creatable = Bool()
    species = ReferenceSet(appearance_id,
                           'SpeciesAppearance.appearance_id',
                           'SpeciesAppearance.species_id',
                           'Species.species_id')
    
    def __init__(self, name, creatable=True):
        self.name = name
        self.creatable = creatable

class SpeciesAppearance(Base):
    __storm_table__ = 'species_appearances'
    __storm_primary__ = 'species_id', 'appearance_id'
    species_id = Int()
    species = Reference(species_id, 'Species.species_id')
    appearance_id = Int()
    appearance = Reference(appearance_id, 'Appearance.appearance_id')
    white_picture_id = Int()
    white_picture = Reference(white_picture_id, 'Picture.picture_id')
    black_picture_id = Int()
    black_picture = Reference(black_picture_id, 'Picture.picture_id')
    
    def __init__(self, species, appearance, white_picture, black_picture):
        self.species = species
        self.appearance = appearance
        self.white_picture = white_picture
        self.black_picture = black_picture
    
    def pil_image_with_color(self, color):
        black_image = self.black_picture.pil_image
        white_image = self.white_picture.pil_image
        if black_image.mode not in ('RGB', 'RGBA'):
            if white_image.mode == 'RGBA':
                black_image = black_image.convert('RGBA')
            else:
                black_image = black_image.convert('RGB')
        if white_image.mode not in ('RGB', 'RGBA'):
            if black_image.mode == 'RGBA':
                white_image = white_image.convert('RGBA')
            else:
                white_image = white_image.convert('RGB')
        if white_image.size != black_image.size:
            white_image = white_image.resize(black_image.size)
        color = [value / 255.0 for value in color]
        if len(color) == 3: # RGB; we want RGBA
            color.append(0.0)
        white_bands = white_image.split()
        black_bands = black_image.split()
        bands = [Image.blend(black_band, white_band, value)
                 for black_band, white_band, value
                     in zip(black_bands, white_bands, color)]
        return Image.merge(white_image.mode, bands)
        
class Pet(Base):
    __storm_table__ = 'pets'
    pet_id = Int(primary=True)
    created = DateTime()
    name = Unicode()
    unformatted_name = Unicode()
    user_id = Int()
    user = Reference(user_id, 'User.user_id')
    species_id = Int()
    species = Reference(species_id, 'Species.species_id')
    appearance_id = Int()
    appearance = Reference(appearance_id, 'Appearance.appearance_id')
    species_appearance = Reference((species_id, appearance_id),
                                   ('SpeciesAppearance.species_id',
                                    'SpeciesAppearance.appearance_id'))
    color_red = Int()
    color_green = Int()
    color_blue = Int()
    
    name_length = 20
    name_regex = re.compile(
        ur'^(?=.{1,%s}$)[ _-]*[A-Za-z][A-Za-z0-9 _-]*$' % name_length)
    
    def __init__(self, name, user, species, appearance, color):
        self.created = datetime.utcnow()
        self.change_name(name)
        self.user = user
        self.species = species
        self.appearance = appearance
        self.color = color
    
    _unformat_name_regex = re.compile(ur'[^a-zA-Z0-9]+')
    @classmethod
    def unformat_name(self, name):
        """Removes formatting from a name."""
        name = self._unformat_name_regex.sub(u'', name)
        name = name.lower()
        return name
    
    def change_name(self, name):
        self.name = name
        self.unformatted_name = self.unformat_name(name)
    
    @classmethod
    def find_pet(cls, name):
        """Finds a pet by name or (stringified) pet ID. Returns None if
        the pet doesn't exist.
        """
        if name.isdigit():
            return cls.get(int(name))
        else:
            name = cls.unformat_name(name)
            return cls.find(unformatted_name=name).one()
    
    def _set_color(self, color):
        self.color_red, self.color_green, self.color_blue = color
    
    def _get_color(self):
        return self.color_red, self.color_green, self.color_blue
    
    color = property(_get_color, _set_color)

class Group(Base):
    __storm_table__ = 'groups'
    group_id = Int(primary=True)
    type = Int(allow_none=False)
    name = Unicode(allow_none=False)
    unformatted_name = Unicode(allow_none=False)
    description = Unicode(allow_none=False)
    owner_user_id = Int(allow_None=False)
    owner = Reference(owner_user_id, 'User.user_id')
    member_count = Int(nullable=False)
    default_role_id = Int(allow_none=False)
    default_role = Reference(default_role_id, 'GroupRole.group_role_id')
    created = DateTime(allow_none=False)
    members = ReferenceSet(group_id, 'GroupMember.group_id')
    member_users = ReferenceSet(group_id,
                                'GroupMember.group_id',
                                'GroupMember.user_id',
                                'User.user_id')
    special_permissions = ReferenceSet(group_id,
                                       'SpecialGroupPermission.group_id')
    
    types_names = [u'Club', u'Guild', u'Cult']
    
    name_length = 30
    name_regex = re.compile(
        ur'^(?=.{1,%s}$)[ _-]*[A-Za-z][A-Za-z0-9 _-]*$' % name_length)
    
    def __init__(self, type, name, description, owner):
        self.type = type
        self.name = name
        self.description = description
        self.owner = owner
        self.member_count = 0
        self.default_role = GroupRole(self, u'Member').save()
        admin_role = GroupRole(self, u'Administrator').save()
        GroupMember(self, owner, admin_role).save()
        self.created = datetime.utcnow()
    
    _unformat_name_regex = re.compile(ur'[^a-zA-Z0-9]+')
    @classmethod
    def unformat_name(self, name):
        """Removes formatting from a name."""
        name = self._unformat_name_regex.sub(u'', name)
        name = name.lower()
        return name

    def change_name(self, name):
        self.name = name
        self.unformatted_name = self.unformat_name(name)

    @classmethod
    def find_group(cls, name):
        """Finds a group by name or (stringified) group ID. Returns None if
        the group doesn't exist.
        """
        if name.isdigit():
            return cls.get(int(name))
        else:
            name = cls.unformat_name(name)
            return cls.find(unformatted_name=name).one()
    
    @classmethod
    def types_can_coexist(cls, type1, type2):
        if type1 is None or type2 is None:
            return True
        if type1 > type2:
            type1, type2 = type2, type1
        if type2 == 2:
            return False
        if type1 == type2 == 1:
            return False
        return True
    
    def can_coexist_with(self, other_type):
        return self.types_can_coexist(self.type, other_type)
    
    @property
    def type_name(self):
        return self.type_names[self.type]

class StandardGroupPermission(Base):
    __storm_table__ = 'standard_group_permissions'
    standard_group_permission_id = Int(primary=True)
    label = Unicode(allow_none=False)
    title = Unicode(allow_none=False)
    description = Unicode(allow_none=False)
    roles = ReferenceSet(standard_group_permission_id,
                         'GroupRoleStandardPermission.standard_group_permission_id',
                         'GroupRoleStandardPermission.group_role_id',
                         'GroupRole.group_role_id')
                         
    def __init__(self, label, title, description):
        self.label = label
        self.title = title
        self.description = description
    
    @classmethod
    def find_label(cls, label, allow_none=False):
        result = cls.find(label=label).one()
        if not allow_none:
            assert result is not None, \
                'Group permission labelled %r not found.' % label
        return result

class SpecialGroupPermission(Base):
    __storm_table__ = 'special_group_permissions'
    special_group_permission_id = Int(primary=True)
    group_id = Int(allow_none=False)
    group = Reference(group_id, 'Group.group_id')
    title = Unicode(allow_none=False)
    roles = ReferenceSet(special_group_permission_id,
                         'GroupRoleSpecialPermission.special_group_permission_id',
                         'GroupRoleSpecialPermission.group_role_id',
                         'GroupRole.group_role_id')
                         
    def __init__(self, group, title):
        self.group = group
        self.title = title

class GroupRole(Base):
    __storm_table__ = 'group_roles'
    group_role_id = Int(primary=True)
    group = Int(allow_none=False)
    name = Unicode(allow_none=False)
    standard_permissions = ReferenceSet(group_role_id,
                                        'GroupRoleStandardPermission.group_role_id',
                                        'GroupRoleStandardPermission.standard_group_permission_id',
                                        'StandardGroupPermission.standard_group_permission_id')
    special_permissions = ReferenceSet(group_role_id,
                                       'GroupRoleSpecialPermission.group_role_id',
                                       'GroupRoleSpecialPermission.special_group_permission_id',
                                       'SpecialGroupPermission.special_group_permission_id')
    
    def __init__(self, group, name):
        self.group = group
        self.name = name
    
    def has_permission(self, permission):
        if isinstance(permission, basestring):
            permission = StandardGroupPermission.find_label(permission)
        if isinstance(permission, StandardGroupPermission):
            return bool(self.standard_permissions.find(
                StandardGroupPermission.standard_group_permission_id \
                    == permission.standard_group_permission_id
            ).count())
        elif isinstance(permission, SpecialGroupPermission):
            return bool(self.special_permissions.find(
                SpecialGroupPermission.special_group_permission_id \
                    == permission.special_group_permission_id
            ).count())
        elif permission is None:
            return True
        else:
            assert False

class GroupRoleStandardPermission(Base):
    __storm_table__ = 'group_role_standard_permissions'
    __storm_primary__ = 'group_role_id', 'standard_group_permission_id'
    group_role_id = Int()
    group_role = Reference(group_role_id, 'GroupRole.group_role_id')
    standard_group_permission_id = Int()
    standard_group_permission = Reference(standard_group_permission_id,
                                          'StandardGroupPermission.standard_group_permission_id')

class GroupRoleSpecialPermission(Base):
    __storm_table__ = 'group_role_special_permissions'
    __storm_primary__ = 'group_role_id', 'special_group_permission_id'
    group_role_id = Int()
    group_role = Reference(group_role_id, 'GroupRole.group_role_id')
    special_group_permission_id = Int()
    special_group_permission = Reference(special_group_permission_id,
                                          'SpecialGroupPermission.special_group_permission_id')

class GroupMember(Base):
    __storm_table__ = 'group_members'
    group_member_id = Int(primary=True)
    user_id = Int(allow_none=False)
    user = Reference(user_id, 'User.user_id')
    group_id = Int(allow_none=False)
    group = Reference(group_id, 'Group.group_id')
    group_role_id = Int(allow_none=False)
    group_role = Reference(group_role_id, 'GroupRole.group_role_id')
    
    def __init__(self, user, group, group_role):
        assert group_role.group == group
        self.user = user
        self.group = group
        self.group_role = group_role

class Forum(Base):
    __storm_table__ = 'forum'
    forum_id = Int(primary=True)
    group_id = Int()
    group = Reference(group_id, 'Group.group_id')
    name = Unicode(allow_none=False)
    order_num = Int()
    
    def __init__(self, name, group=None):
        self.name = name
        self.group = group
        
    def __storm_flushed__(self):
        self.order_num = self.forum_id