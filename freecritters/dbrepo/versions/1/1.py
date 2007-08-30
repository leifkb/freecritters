from sqlalchemy import *
from migrate import *

def _foreign_key(name):
    """Shortcut for a cascaded foreign key."""
    
    return ForeignKey(name, onupdate='CASCADE', ondelete='CASCADE')

metadata = BoundMetaData(migrate_engine)

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

species = Table('species', metadata,
    Column('species_id', Integer, primary_key=True),
    Column('name', Unicode, nullable=False, index=True),
    Column('creatable', Boolean, nullable=False)
)

appearances = Table('appearances', metadata,
    Column('appearance_id', Integer, primary_key=True),
    Column('name', Unicode, nullable=False),
    Column('creatable', Boolean, nullable=False)
)

species_appearances = Table('species_appearances', metadata,
    Column('species_appearance_id', Integer, primary_key=True),
    Column('species_id', Integer, _foreign_key('species.species_id'), index=True, nullable=False),
    Column('appearance_id', Integer,_foreign_key('appearances.appearance_id'), nullable=False),
    Column('white_picture_id', Integer, ForeignKey('pictures.picture_id'), nullable=False),
    Column('black_picture_id', Integer, ForeignKey('pictures.picture_id'), nullable=False),
    UniqueConstraint('species_id', 'appearance_id')
)
Index('idx_speciesappearances_speciesid_appearanceid',
    species_appearances.c.species_id,
    species_appearances.c.appearance_id
)

pets = Table('pets', metadata,
    Column('pet_id', Integer, primary_key=True),
    Column('created', DateTime(timezone=False), nullable=False),
    Column('name', Unicode, nullable=False),
    Column('unformatted_name', Unicode, index=True, unique=True, nullable=False),
    Column('user_id', Integer, _foreign_key('users.user_id'), index=True, nullable=False),
    Column('species_appearance_id', Integer, ForeignKey('species_appearances.species_appearance_id'), nullable=False),
    Column('color_red', Integer, nullable=False),
    Column('color_green', Integer, nullable=False),
    Column('color_blue', Integer, nullable=False)
)

tables = [
    roles, users, subaccounts, logins, form_tokens, mail_conversations,
    mail_participants, mail_messages, permissions, role_permissions,
    subaccount_permissions, pictures, resized_pictures, species, appearances,
    species_appearances, pets
]

def upgrade():
    for table in tables:
        table.create()
    
    default_role_id = roles.insert().execute(
        label=u'default',
        name=u'User'
    ).last_inserted_ids()[0]
    
    default_permissions_ids = []
    
    permissions_to_add = [
        (u'edit_profile', u'Edit profile', u'Allows profile editing.'),
        (u'view_mail', u'View mail', u'Allows mail to be viewed.'),
        (u'send_mail', u'Send mail',
         u'Allows mail to be sent and replied to.'),
        (u'delete_mail', u'Delete mail', u'Allows mail to be deleted.'),
        (u'create_pet', u'Create pet', u'Allows pets to be created.')
    ]
    
    for label, title, description in permissions_to_add:
        permission_id = permissions.insert().execute(
            label=label,
            title=title,
            description=description
        ).last_inserted_ids()[0]
        role_permissions.insert().execute(
            role_id=default_role_id,
            permission_id=permission_id
        )
    
def downgrade():
    for table in tables:
        table.drop()
