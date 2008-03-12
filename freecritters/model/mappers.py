from sqlalchemy.orm import relation, backref, dynamic_loader
from sqlalchemy import and_, select
from freecritters.model.tables import \
    users, subaccounts, logins, form_tokens, mail_conversations, \
    mail_participants, mail_messages, permissions, roles, role_permissions, \
    subaccount_permissions, pictures, resized_pictures, species, appearances, \
    species_appearances, pets, groups, standard_group_permissions, \
    special_group_permissions, group_roles, group_role_standard_permissions, \
    group_role_special_permissions, group_members, forums, threads, posts
from freecritters.model.session import Session
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
from freecritters.model.pet import Pet
from freecritters.model.group import Group
from freecritters.model.standardgrouppermission import StandardGroupPermission
from freecritters.model.specialgrouppermission import SpecialGroupPermission
from freecritters.model.grouprole import GroupRole
from freecritters.model.groupmember import GroupMember
from freecritters.model.forum import Forum
from freecritters.model.thread import Thread
from freecritters.model.post import Post
from freecritters.model.util import FieldCopierExtension, CountKeeperExtension

mapper = Session.mapper

mapper(User, users, properties={
    'role': relation(Role, backref=backref('users', lazy='dynamic'))
})

mapper(Subaccount, subaccounts, properties={
    'user': relation(User, backref=backref('subaccounts', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True)),
    'permissions': relation(Permission, secondary=subaccount_permissions, backref=backref('subaccounts'))
})

mapper(Login, logins, properties={
    'user': relation(User, backref=backref('logins', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True)),
    'subaccount': relation(Subaccount, backref=backref('logins', lazy='dynamic', cascade='all', passive_deletes=True))
})

mapper(FormToken, form_tokens, properties={
    'user': relation(User, backref=backref('form_tokens', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True)),
    'subaccount': relation(Subaccount, backref=backref('form_tokens', lazy='dynamic', cascade='all', passive_deletes=True))
})

mapper(MailConversation, mail_conversations)

mapper(MailParticipant, mail_participants, properties={
    'conversation': relation(MailConversation, lazy=False, join_depth=2,
        backref=backref('participants', lazy=False, join_depth=2, cascade='all, delete-orphan', passive_deletes=True)),
    'user': relation(User, backref=backref('mail_participations', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True))
})

mapper(MailMessage, mail_messages, properties={
    'conversation': relation(MailConversation, backref=backref('messages', lazy='dynamic', cascade='all', passive_deletes=True)),
    'user': relation(User, backref=backref('mail_messages', lazy='dynamic', cascade='all', passive_deletes=True))
})

mapper(Permission, permissions)

mapper(Role, roles, properties={
    'permissions': relation(Permission, secondary=role_permissions, backref=backref('roles'))
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
     'white_picture': relation(Picture, primaryjoin=pictures.c.picture_id==species_appearances.c.white_picture_id, backref=backref('species_appearances_white', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True, primaryjoin=pictures.c.picture_id==species_appearances.c.white_picture_id)),
     'black_picture': relation(Picture, primaryjoin=pictures.c.picture_id==species_appearances.c.black_picture_id, backref=backref('species_appearances_black', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True, primaryjoin=pictures.c.picture_id==species_appearances.c.black_picture_id))
})

mapper(Pet, pets, properties={
    'user': relation(User, backref=backref('pets', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True)),
    'species_appearance': relation(SpeciesAppearance, backref=backref('pets', lazy='dynamic'))
})

mapper(Group, groups, properties={
    'owner': relation(User, backref=backref('owner_groups', lazy='dynamic')),
})

mapper(StandardGroupPermission, standard_group_permissions, properties={
    'roles': relation(GroupRole, secondary=group_role_standard_permissions, backref=backref('standard_permissions', passive_deletes=True), lazy='dynamic')
})

mapper(SpecialGroupPermission, special_group_permissions, properties={
    'group': relation(Group, backref=backref('special_permissions', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True)),
    'roles': relation(GroupRole, secondary=group_role_special_permissions, backref=backref('special_permissions', passive_deletes=True), lazy='dynamic')
})

mapper(GroupRole, group_roles, properties={
    'group': relation(Group, backref=backref('roles', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True))
})

mapper(GroupMember, group_members, properties={
    'user': relation(User, backref=backref('group_memberships', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True)),
    'group': relation(Group, backref=backref('members', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True)),
    'group_role': relation(GroupRole, backref=backref('members', lazy='dynamic'))
}, extension=CountKeeperExtension('group', 'member_count'))

mapper(Forum, forums, properties={
    'group': relation(Group, backref=backref('forums', lazy='dynamic', cascade='all', passive_deletes=True)),
    'view_permission': relation(Permission, primaryjoin=forums.c.view_permission_id==permissions.c.permission_id, backref=backref('forums_view', primaryjoin=forums.c.view_permission_id==permissions.c.permission_id, lazy='dynamic', passive_deletes=True)),
    'view_group_permission': relation(SpecialGroupPermission, primaryjoin=forums.c.view_special_group_permission_id==special_group_permissions.c.special_group_permission_id, backref=backref('forums_view', primaryjoin=forums.c.view_special_group_permission_id==special_group_permissions.c.special_group_permission_id, lazy='dynamic', passive_deletes=True)),
    'create_thread_permission': relation(Permission, primaryjoin=forums.c.create_thread_permission_id==permissions.c.permission_id, backref=backref('forums_create_thread', primaryjoin=forums.c.create_thread_permission_id==permissions.c.permission_id, lazy='dynamic', passive_deletes=True)),
    'create_thread_group_permission': relation(SpecialGroupPermission, primaryjoin=forums.c.create_thread_special_group_permission_id==special_group_permissions.c.special_group_permission_id, backref=backref('forums_create_thread', primaryjoin=forums.c.create_thread_special_group_permission_id==special_group_permissions.c.special_group_permission_id, lazy='dynamic', passive_deletes=True)),
    'create_post_permission': relation(Permission, primaryjoin=forums.c.create_post_permission_id==permissions.c.permission_id, backref=backref('forums_create_post', primaryjoin=forums.c.create_post_permission_id==permissions.c.permission_id, lazy='dynamic', passive_deletes=True)),
    'create_post_group_permission': relation(SpecialGroupPermission, primaryjoin=forums.c.create_post_special_group_permission_id==special_group_permissions.c.special_group_permission_id, backref=backref('forums_create_post', primaryjoin=forums.c.create_post_special_group_permission_id==special_group_permissions.c.special_group_permission_id, lazy='dynamic', passive_deletes=True))
}, extension=FieldCopierExtension(forum_id='order_num'))

mapper(Thread, threads, properties={
    'forum': relation(Forum, backref=backref('threads', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True)),
    'user': relation(User, backref=backref('threads', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True))
}, extension=CountKeeperExtension('forum', 'thread_count'))

mapper(Post, posts, properties={
    'thread': relation(Thread, backref=backref('posts', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True)),
    'user': relation(User, backref=backref('posts', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True)),
    'membership': relation(GroupMember, foreign_keys=[posts.c.thread_id], primaryjoin=and_(group_members.c.user_id==posts.c.user_id, group_members.c.group_id==select([forums.c.group_id], and_(forums.c.forum_id==threads.c.forum_id, threads.c.thread_id==posts.c.thread_id), [forums, threads])), viewonly=True)
}, extension=CountKeeperExtension('thread', 'post_count'))