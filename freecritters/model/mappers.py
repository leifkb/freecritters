from sqlalchemy.orm import mapper, relation, backref, dynamic_loader

from freecritters.model.tables import \
    users, subaccounts, logins, form_tokens, mail_conversations, \
    mail_participants, mail_messages, permissions, roles, role_permissions, \
    subaccount_permissions, pictures, resized_pictures, species, appearances, \
    species_appearances, groups, standard_group_permissions, \
    special_group_permissions, group_roles, group_role_standard_permissions, \
    group_role_special_permissions, group_members, forums
from freecritters.model.user import User
from freecritters.model.subaccount import Subaccount
from freecritters.model.login import Login
from freecritters.model.formtoken import FormToken
from freecritters.model.mailconversation import MailConversation
from freecritters.model.mailparticipant import MailParticipant
from freecritters.model.mailmessage import MailMessage
from freecritters.model.permission import Permission
from freecritters.model.role import Role
from freecritters.model.picture import Picture
from freecritters.model.resizedpicture import ResizedPicture
from freecritters.model.species import Species
from freecritters.model.appearance import Appearance
from freecritters.model.speciesappearance import SpeciesAppearance
from freecritters.model.group import Group
from freecritters.model.standardgrouppermission import StandardGroupPermission
from freecritters.model.specialgrouppermission import SpecialGroupPermission
from freecritters.model.grouprole import GroupRole
from freecritters.model.groupmember import GroupMember
from freecritters.model.forum import Forum
from freecritters.model.util import FieldCopierExtension

mapper(User, users, properties={
    'role': relation(Role, backref=backref('users', lazy='dynamic'))
})

mapper(Subaccount, subaccounts, properties={
    'user': relation(User, backref=backref('subaccounts', lazy='dynamic')),
    'permissions': dynamic_loader(Permission, secondary=subaccount_permissions, backref=backref('subaccounts', lazy='dynamic'))
})

mapper(Login, logins, properties={
    'user': relation(User, backref=backref('logins', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True)),
    'suabccount': relation(Subaccount, backref=backref('logins', lazy='dynamic', cascade='all', passive_deletes=True))
})

mapper(FormToken, form_tokens, properties={
    'user': relation(User, backref=backref('form_tokens', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True)),
    'suabccount': relation(Subaccount, backref=backref('form_tokens', lazy='dynamic', cascade='all', passive_deletes=True))
})

mapper(MailConversation, mail_conversations)

mapper(MailParticipant, mail_participants, properties={
    'conversation': relation(MailConversation, lazy=False,
        backref=backref('participants', lazy=False, cascade='all, delete-orphan', passive_deletes=True)),
    'user': relation(User, backref=backref('mail_participations', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True))
})

mapper(MailMessage, mail_messages, properties={
    'conversation': relation(MailConversation, backref=backref('messages', lazy='dynamic', cascade='all', passive_deletes=True)),
    'user': relation(User, backref=backref('mail_messages', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True))
})

mapper(Permission, permissions)

mapper(Role, roles, properties={
    'permissions': dynamic_loader(Permission, secondary=subaccount_permissions, backref=backref('roles', lazy='dynamic'))
})

mapper(Picture, pictures)

mapper(ResizedPicture, resized_pictures, properties={
    'pictures': relation(Picture, backref=backref('resized_pictures', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True))
})

mapper(Species, species)

mapper(Appearance, appearances)

mapper(SpeciesAppearance, species_appearances, properties={
    'species': relation(Species, backref=backref('species_appearances', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True)),
    'appearance': relation(Appearance, backref=backref('species_appearances', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True)),
     'white_picture': relation(Picture, primaryjoin=pictures.c.picture_id==species_appearances.c.white_picture_id, backref=backref('species_appearances_white', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True)),
     'black_picture': relation(Picture, primaryjoin=pictures.c.picture_id==species_appearances.c.white_picture_id, backref=backref('species_appearances_black', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True))
})

mapper(Group, groups, properties={
    'owner': relation(User, backref=backref('owner_groups', lazy='dynamic')),
    'default_role': relation(GroupRole)
})

mapper(StandardGroupPermission, standard_group_permissions, properties={
    'roles': relation(Role, secondary=group_role_standard_permissions, backref=backref('standard_permission', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True))
})

mapper(SpecialGroupPermission, special_group_permissions, properties={
    'group': relation(Group, backref=backref('special_permissions', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True)),
    'roles': relation(Role, secondary=group_role_special_permissions, backref=backref('special_permissions', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True))
})

mapper(GroupRole, group_roles, properties={
    'group': relation(Group, backref=backref('roles', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True))
})

mapper(GroupMember, group_members, properties={
    'user': relation(User, backref=backref('group_memberships', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True)),
    'group': relation(Group, backref=backref('groups', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True)),
    'role': relation(GroupRole, backref=backref('members', lazy='dynamic'))
})

mapper(Forum, forums, properties={
    'group': relation(Group, backref=backref('forums', lazy='dynamic', cascade='all', passive_deletes=True))
}, extension=FieldCopierExtension(forum_id='order_num'))