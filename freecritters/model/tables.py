from sqlalchemy import Table, Column, Integer, DateTime, MetaData, \
                       ForeignKey, Unicode, Binary, UniqueConstraint, \
                       ForeignKeyConstraint, Index, Boolean, String

metadata = MetaData()

def _foreign_key(col, name):
    """Shortcut for a cascaded foreign key."""
    
    return ForeignKey(col, name=name, use_alter=True, onupdate='CASCADE', ondelete='CASCADE')

users = Table('users', metadata,
    Column('user_id', Integer, primary_key=True, nullable=False),
    Column('username', Unicode, nullable=False),
    Column('unformatted_username', Unicode, nullable=False),
    Column('password', Binary(20), nullable=False),
    Column('salt', Binary(4), nullable=False),
    Column('profile', Unicode, nullable=False),
    Column('rendered_profile', Unicode, nullable=False),
    Column('money', Integer, nullable=False),
    Column('registration_date', DateTime(timezone=False), nullable=False),
    Column('pre_mail_message', Unicode),
    Column('last_inbox_view', DateTime(timezone=False)),
    Column('role_id', Integer, ForeignKey('roles.role_id', name='fkey__users__role_id'), nullable=False),
    UniqueConstraint('unformatted_username', name='uniq__users__unformatted_username')
)

subaccounts = Table('subaccounts', metadata,
    Column('subaccount_id', Integer, primary_key=True, nullable=False),
    Column('user_id', Integer, _foreign_key('users.user_id', 'fkey__subaccounts__user_id'), nullable=False),
    Column('name', Unicode, nullable=False),
    Column('password', Binary(20), nullable=False),
    Column('salt', Binary(4), nullable=False),
    UniqueConstraint('user_id', 'name', name='uniq__subaccounts__user_id__name')
)
Index('idx__subaccounts__user_id__name', subaccounts.c.user_id, subaccounts.c.name)

logins = Table('logins', metadata,
    Column('login_id', Integer, primary_key=True, nullable=False),
    Column('code', Unicode, nullable=False),
    Column('creation_time', DateTime(timezone=False), nullable=False),
    Column('user_id', Integer, _foreign_key('users.user_id', 'fkey__logins__user_id'), nullable=False),
    Column('subaccount_id', Integer, _foreign_key('subaccounts.subaccount_id', 'fkey__logins__subaccount_id'))
)
Index('idx__logins__user_id', logins.c.user_id)
Index('idx__logins__subaccount_id', logins.c.subaccount_id)

form_tokens = Table('form_tokens', metadata,
    Column('form_token_id', Integer, primary_key=True, nullable=False),
    Column('token', Unicode, nullable=False),
    Column('creation_time', DateTime(timezone=False), nullable=False),
    Column('user_id', Integer, _foreign_key('users.user_id', 'fkey__form_tokens__user_id'), nullable=False),
    Column('subaccount_id', Integer, _foreign_key('subaccounts.subaccount_id', 'fkey__subaccounts__subaccount_id'))
)
Index('idx__form_tokens__creation_time', form_tokens.c.creation_time)
Index('idx__form_tokens__subaccount_id', form_tokens.c.subaccount_id)
Index('idx__form_tokens__user_id__subaccount_id__creation_time__token',
      form_tokens.c.user_id, form_tokens.c.subaccount_id,
      form_tokens.c.creation_time, form_tokens.c.token)

mail_conversations = Table('mail_conversations', metadata,
    Column('conversation_id', Integer, primary_key=True, nullable=False),
    Column('subject', Unicode, nullable=False),
    Column('creation_time', DateTime(timezone=False), nullable=False)
)

mail_participants = Table('mail_participants', metadata,
    Column('participant_id', Integer, primary_key=True, nullable=False),
    Column('conversation_id', Integer,
           _foreign_key('mail_conversations.conversation_id', 'mail_participants.conversation_id'),
           nullable=False),
    Column('user_id', Integer, _foreign_key('users.user_id', 'fkey__mail_participants__user_id')),
    Column('last_change', DateTime(timezone=False), nullable=False),
    Column('last_view', DateTime(timezone=False)),
    Column('deleted', Boolean, nullable=False),
    Column('system', Boolean, nullable=False),
    UniqueConstraint('conversation_id', 'user_id', name='uniq__mail_participants__conversation_id__user_id')
)
Index('idx__mail_participants__conversation_id', mail_participants.c.conversation_id)
Index('idx__mail_participants__user_id__deleted__last_change',
      mail_participants.c.user_id, mail_participants.c.deleted,
      mail_participants.c.last_change
)
Index('idx__mail_participants__user_id__deleted__system__last_change',
      mail_participants.c.user_id, mail_participants.c.deleted,
      mail_participants.c.system, mail_participants.c.last_change
)

mail_messages = Table('mail_messages', metadata,
    Column('message_id', Integer, primary_key=True, nullable=False),
    Column('conversation_id', Integer,
           _foreign_key('mail_conversations.conversation_id', 'fkey__mail_messages__conversation_id'),
           nullable=False),
    Column('user_id', Integer, _foreign_key('users.user_id', 'fkey__mail_messages__user_id'), nullable=True),
    Column('message', Unicode, nullable=False),
    Column('rendered_message', Unicode, nullable=False),
    Column('sent', DateTime(timezone=False), nullable=False)
)
Index('idx__mail_messages__conversation_id__sent',
      mail_messages.c.conversation_id,
      mail_messages.c.sent
)

permissions = Table('permissions', metadata,
    Column('permission_id', Integer, primary_key=True, nullable=False),
    Column('label', Unicode, nullable=True),
    Column('title', Unicode, nullable=False),
    Column('description', Unicode, nullable=False),
    UniqueConstraint('label', name='uniq__permissions__label')
)

roles = Table('roles', metadata,
    Column('role_id', Integer, primary_key=True, nullable=False),
    Column('label', Unicode, nullable=True),
    Column('name', Unicode, nullable=False),
    UniqueConstraint('label', name='uniq__roles__label')
)

role_permissions = Table('role_permissions', metadata,
    Column('role_id', Integer, _foreign_key('roles.role_id', 'fkey__role_permissions__role_id'),
           primary_key=True),
    Column('permission_id', Integer,
           _foreign_key('permissions.permission_id', 'fkey__role_permissions__permission_id'),
           primary_key=True)
)

subaccount_permissions = Table('subaccount_permissions', metadata,
    Column('subaccount_id', Integer,
           _foreign_key('subaccounts.subaccount_id', 'fkey__subaccount_permissions__subaccount_id'),
           primary_key=True),
    Column('permission_id', Integer,
           _foreign_key('permissions.permission_id', 'fkey__subaccount_permissions__permission_id'),
           primary_key=True)
)

pictures = Table('pictures', metadata,
    Column('picture_id', Integer, primary_key=True),
    Column('added', DateTime(timezone=False), nullable=False),
    Column('last_change', DateTime(timezone=False), nullable=False),
    Column('name', Unicode, nullable=False),
    Column('copyright', Unicode, nullable=False),
    Column('description', Unicode, nullable=False),
    Column('width', Integer, nullable=False),
    Column('height', Integer, nullable=False),
    Column('format', String, nullable=False),
    Column('image', Binary, nullable=False)
)

resized_pictures = Table('resized_pictures', metadata,
    Column('resized_picture_id', Integer, primary_key=True),
    Column('picture_id', Integer, _foreign_key('pictures.picture_id', 'fkey__resized_pictures__picture_id'),
           nullable=False),
    Column('added', DateTime(timezone=False), nullable=False),
    Column('width', Integer, nullable=False),
    Column('height', Integer, nullable=False),
    Column('image', Binary, nullable=False)
)
Index('idx__resized_pictures__picture_id__width__height',
    resized_pictures.c.picture_id,
    resized_pictures.c.width,
    resized_pictures.c.height
)

species = Table('species', metadata,
    Column('species_id', Integer, primary_key=True),
    Column('name', Unicode, nullable=False),
    Column('creatable', Boolean, nullable=False)
)
Index('idx__species__name', species.c.name)

appearances = Table('appearances', metadata,
    Column('appearance_id', Integer, primary_key=True),
    Column('name', Unicode, nullable=False),
    Column('creatable', Boolean, nullable=False)
)

species_appearances = Table('species_appearances', metadata,
    Column('species_appearance_id', Integer, primary_key=True),
    Column('species_id', Integer, _foreign_key('species.species_id', 'fkey__species_appearances__species_id'), nullable=False),
    Column('appearance_id', Integer,
           _foreign_key('appearances.appearance_id', 'fkey__species_appearances__appearance_id'),
           nullable=False),
    Column('white_picture_id', Integer,
           ForeignKey('pictures.picture_id', name='fkey__species_appearances__white_picture_id'),
           nullable=False),
    Column('black_picture_id', Integer,
           ForeignKey('pictures.picture_id', name='fkey__species_appearances__black_picture_id'),
           nullable=False),
    Column('last_change', DateTime(timezone=False), nullable=False),
    UniqueConstraint('species_id', 'appearance_id', name='uniq__species_appearances__species_id__appearance_id')    
)
Index('idx__species_appearances__species_id__appearance_id',
    species_appearances.c.species_id,
    species_appearances.c.appearance_id
)

pets = Table('pets', metadata,
    Column('pet_id', Integer, primary_key=True),
    Column('created', DateTime(timezone=False), nullable=False),
    Column('name', Unicode, nullable=False),
    Column('unformatted_name', Unicode, nullable=False),
    Column('user_id', Integer, _foreign_key('users.user_id', 'fkey__pets__user_id'), nullable=False),
    Column('species_appearance_id', Integer, ForeignKey('species_appearances.species_appearance_id', name='fkey__pets__species_appearance_id'), nullable=False),
    Column('color_red', Integer, nullable=False),
    Column('color_green', Integer, nullable=False),
    Column('color_blue', Integer, nullable=False),
    UniqueConstraint('unformatted_name', name='uniq__pets__unformatted_name')
)
Index('idx__pets__user_id', pets.c.user_id)

groups = Table('groups', metadata,
    Column('group_id', Integer, primary_key=True),
    Column('created', DateTime(timezone=False), nullable=False),
    Column('type', Integer, nullable=False),
    Column('name', Unicode, nullable=False),
    Column('unformatted_name', Unicode, nullable=False),
    Column('description', Unicode, nullable=False),
    Column('home_page', Unicode, nullable=False),
    Column('rendered_home_page', Unicode, nullable=False),
    Column('owner_user_id', Integer, _foreign_key('users.user_id', name='fkey__groups__owner_user_id'), nullable=False),
    Column('member_count', Integer, nullable=False),
    UniqueConstraint('unformatted_name', name='uniq__groups__unformatted_name')
)
Index('idx__groups__type', groups.c.type)
Index('idx__groups__name', groups.c.name)
Index('idx__groups__owner_user_id', groups.c.owner_user_id)
Index('idx__groups__member_count', groups.c.member_count)

standard_group_permissions = Table('standard_group_permissions', metadata,
    Column('standard_group_permission_id', Integer, primary_key=True),
    Column('label', Unicode, nullable=False),
    Column('title', Unicode, nullable=False),
    Column('description', Unicode, nullable=False),
    UniqueConstraint('label', name='uniq__standard_group_permissions__label')
)

special_group_permissions = Table('special_group_permissions', metadata,
    Column('special_group_permission_id', Integer, primary_key=True),
    Column('group_id', Integer, _foreign_key('groups.group_id', 'fkey__special_group_permissions__group_id'),
           nullable=False),
    Column('title', Unicode, nullable=False)
)
Index('idx__special_group_permissions__group_id', special_group_permissions.c.group_id)

group_roles = Table('group_roles', metadata,
    Column('group_role_id', Integer, primary_key=True),
    Column('group_id', Integer, _foreign_key('groups.group_id', 'fkey__group_roles__group_id'), nullable=False),
    Column('name', Unicode, nullable=False),
    Column('is_default', Boolean, nullable=False),
)
Index('idx__group_roles__group_id__is_default', group_roles.c.group_id, group_roles.c.is_default)

group_role_standard_permissions = Table('group_role_standard_permissions', metadata,
    Column('group_role_id', Integer,
           _foreign_key('group_roles.group_role_id', 'fkey__group_role_standard_permissions__group_role_id'),
           primary_key=True),
    Column('standard_group_permission_id', Integer,
           _foreign_key('standard_group_permissions.standard_group_permission_id',
                        'fkey__group_role_standard_permissions__standard_group_permission_id'),
           primary_key=True)
)

group_role_special_permissions= Table('group_role_special_permissions', metadata,
    Column('group_role_id', Integer,
           _foreign_key('group_roles.group_role_id', 'fkey__group_role_special_permissions__group_role_id'),
           primary_key=True),
    Column('special_group_permission_id', Integer,
           _foreign_key('special_group_permissions.special_group_permission_id',
                        'fkey__group_role_special_permissions__special_group_permission_id'),
           primary_key=True)
)

group_members = Table('group_members', metadata,
    Column('group_member_id', Integer, primary_key=True),
    Column('user_id', Integer, _foreign_key('users.user_id', 'fkey__group_members__user_id'), nullable=False),
    Column('group_id', Integer, _foreign_key('groups.group_id', 'fkey__group_members__group_id'), nullable=False),
    Column('group_role_id', Integer, _foreign_key('group_roles.group_role_id', 'fkey__group_members__group_role_id'),
           nullable=False),
    Column('joined', DateTime(timezone=False), nullable=False),
    UniqueConstraint('user_id', 'group_id', name='uniq__group_members__user_id__group_id')
)
Index('idx__group_members__group_id__user_id',
      group_members.c.group_id,
      group_members.c.user_id
)

#group_bannings = Table('group_bannings', metadata,
#    Column('group_banning_id', Integer, primary_key=True),
#    Column('user_id', Integer, _foreign_key('users.user_id', 'fkey__group_bannings__user_id'), nullable=False),
#    Column('group_id', Integer, _foreign_key('groups.group_id', 'fkey__group_bannings__group_id'), nullable=False),
#    Column('reason', 

forums = Table('forums', metadata,
    Column('forum_id', Integer, primary_key=True),
    Column('group_id', Integer, _foreign_key('groups.group_id', 'fkey__forums__group_id')),
    Column('name', Unicode, nullable=False),
    Column('order_num', Integer),
    Column('thread_count', Integer, nullable=False),
    Column('view_permission_id', Integer, _foreign_key('permissions.permission_id', 'fkey__forums__view_permission_id')),
    Column('view_special_group_permission_id', Integer, _foreign_key('special_group_permissions.special_group_permission_id', 'fkey__forums__view_special_group_permission_id')),
    Column('create_thread_permission_id', Integer, ForeignKey('permissions.permission_id', 'fkey__forums__create_thread_permission_id')),
    Column('create_thread_special_group_permission_id', Integer, _foreign_key('special_group_permissions.special_group_permission_id', 'fkey__forums__create_thread_special_group_permission_id')),
    Column('create_post_permission_id', Integer, _foreign_key('permissions.permission_id', 'fkey__forums__create_post_permission_id')),
    Column('create_post_special_group_permission_id', Integer, _foreign_key('special_group_permissions.special_group_permission_id', 'fkey__forums__create_post_special_group_permission_id')),
)
Index('idx__forums__group_id__order_num',
    forums.c.group_id,
    forums.c.order_num
)

threads = Table('threads', metadata,
    Column('thread_id', Integer, primary_key=True),
    Column('forum_id', Integer, _foreign_key('forums.forum_id', 'fkey__threads__forum_id'), nullable=False),
    Column('user_id', Integer, _foreign_key('users.user_id', 'fkey__threads__user_id'), nullable=False),
    Column('subject', Unicode, nullable=False),
    Column('created', DateTime(timezone=False), nullable=False),
    Column('post_count', Integer, nullable=False),
    Column('last_post', DateTime(timezone=False))
)
Index('idx__threads__forum_id__last_post',
    threads.c.forum_id,
    threads.c.last_post
)

posts = Table('posts', metadata,
    Column('post_id', Integer, primary_key=True),
    Column('thread_id', Integer, _foreign_key('threads.thread_id', 'fkey__posts__thread_id'), nullable=False),
    Column('user_id', Integer, _foreign_key('users.user_id', 'fkey__posts__user_id'), nullable=False),
    Column('message', Unicode, nullable=False),
    Column('rendered_message', Unicode, nullable=False),
    Column('created', DateTime(timezone=False), nullable=False)
)
Index('idx__posts__thread_id__created',
    posts.c.thread_id,
    posts.c.created
)
Index('idx__posts__user_id__created',
    posts.c.user_id,
    posts.c.created
)