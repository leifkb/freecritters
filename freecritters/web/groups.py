# -*- coding: utf-8 -*-

from freecritters.web.form import \
    Form, SelectMenu, TextField, TextArea, HiddenField, SubmitButton, \
    CheckBoxes, LengthValidator, RegexValidator, SpecificValueValidator, \
    NotBlankValidator
from sqlalchemy import asc, desc
from sqlalchemy.orm import eagerload
from freecritters.model import Session, User, Group, GroupMember, GroupRole, \
                               MailConversation, MailParticipant, MailMessage, \
                               Forum, SpecialGroupPermission, \
                               StandardGroupPermission
from freecritters.web.paginator import Paginator
from freecritters.web.modifiers import \
    FormTokenField, GroupNameNotTakenValidator, GroupTypeCompatibilityValidator, \
    HtmlModifier
from freecritters.web.globals import fc
from freecritters.textformats import render_plain_text
from freecritters.web.exceptions import Error403, Error404
from freecritters.model.util import set_dynamic_relation
from freecritters.web.util import confirm

description_field = TextArea(
    u'description', u'Description',
    u'Plain text. Limited to %s characters.' % Group.max_description_length,
    rows=10,
    modifiers=[LengthValidator(10, Group.max_description_length)])
         
create_group_form = Form(u'post', 'groups.create_group',
    FormTokenField(),
    TextField(u'name', u'Name', max_length=Group.name_length,
              modifiers=[RegexValidator(Group.name_regex,
                                        message=u'Can only contain '
                                                u'letters, numbers, '
                                                u'spaces, hyphens, and '
                                                u'underscores. Can not '
                                                u'start with a number.'),
                         GroupNameNotTakenValidator()]),
    SelectMenu(u'type', u'Type', options=list(enumerate(Group.type_names)),
               modifiers=[GroupTypeCompatibilityValidator()]),
    description_field,
    SubmitButton(title=u'Create', id_=u'createbtn'))

def create_group(req):
    req.check_permission(u'groups')
    
    owned_group_count = Group.query.filter_by(owner_user_id=req.user.user_id).count()
    max_ownable_count = req.config.groups.ownable_per_user
    if max_ownable_count is not None and owned_group_count >= max_ownable_count:
        return req.render_template('too_many_owned_groups.mako',
            owned_group_count=owned_group_count,
            max_ownable_count=max_ownable_count)
    
    results = create_group_form(req)
    if results.successful:
        group = Group(results[u'type'], results[u'name'], results[u'description'], req.user)
        Session.save(group)
        Session.flush()
        req.redirect('groups.group', group_id=group.group_id)
    else:
        return req.render_template('create_group_form.mako',
            form=results)

def groups(req):
    req.check_permission(u'groups')

    return req.render_template('groups.mako',
        groups=req.user.group_list)

orders = {
    u'members': desc(Group.member_count),
    u'newest': desc(Group.created),
    u'oldest': asc(Group.created)
}

order_names = [
    (u'members', u'Most members'),
    (u'newest', u'Newest'),
    (u'oldest', u'Oldest')
]

group_list_sort_form = Form(u'get', 'groups.group_list',
    SelectMenu(u'order', u'Sort by', options=order_names),
    SubmitButton(title=u'Sort', id_=u'submit'),
    id_prefix=u'sort_')

group_list_paginator = Paginator(15)

def group_list(req):
    req.check_permission(u'groups')
    
    results = group_list_sort_form(req, {u'order': u'members'})
    order = orders[results[u'order']]
    
    groups = Group.query.options(eagerload('owner')).order_by(order)
    paginated = group_list_paginator(req, groups)

    return req.render_template('group_list.mako',
        max_group_type=req.user.max_group_type,
        groups=paginated.all(),
        sort_form=results,
        paginator=paginated
    )

join_form = Form(u'post', None,
    FormTokenField(),
    SubmitButton(title=u'Join', id_=u'submit'))

def group(req, group_id):
    group = Group.query.get(group_id)
    if group is None:
        return None
    req.check_permission(u'groups')
    membership = req.user.group_memberships.filter_by(group_id=group.group_id).first()
    if membership is None:
        is_member = False
        if group.can_coexist_with(req.user.max_group_type):
            join_results = join_form(req)
            join_results.action = 'groups.group', dict(group_id=group.group_id)
            if join_results.successful:
                membership = GroupMember(req.user, group, group.default_role)
                Session.save(membership)
                join_results = None
                is_member = True
        else:
            join_results = None
    else:
        join_results = None
        is_member = True
    
    fc.is_member = is_member # Kludge to allow dynamic inheritance
    
    return req.render_template('group.mako',
        group=group,
        is_member=is_member,
        join_form=join_results)


def leave_group(req, group_id):
    group = Group.query.get(group_id)
    if group is None:
        return None
    req.check_group_permission(group, None)
    
    if req.user == group.owner:
        return req.render_template('cant_leave_group.mako',
            group=group)
    
    confirm(u'leave this group')
    
    membership = req.user.find_group_membership(group)
    Session.delete(membership)
    req.redirect('groups', left=1)

group_member_paginator = Paginator()

def group_members(req, group_id):
    group = Group.query.get(group_id)
    if group is None:
        return None
    req.check_group_permission(group, None)
    
    members = group.members.join('user').options(eagerload('user'), eagerload('group_role')).order_by([
        desc(User.user_id==group.owner_user_id),
        desc(GroupMember.joined)
    ])
    paginated = group_member_paginator(req, members)
    
    return req.render_template('group_members.mako',
        group=group,
        paginator=paginated,
        members=paginated.all())

def _group_and_membership(group_id, username):
    group = Group.query.get(group_id)
    if group is None:
        raise Error404()
    user = User.find_user(username)
    if user is None:
        raise Error404()
    membership = group.members.join('user').filter_by(user_id=user.user_id).first()
    if membership is None:
        raise Error404()
    return group, membership

def edit_member(req, group_id, username):
    group, membership = _group_and_membership(group_id, username)
    req.check_group_permission(group, u'edit_members')
    
    role_options = list(
        (role, role.name)
        for role in group.roles.order_by(GroupRole.name)
    )
    
    form = Form(u'post', ('groups.edit_member', dict(group_id=group.group_id, username=membership.user.unformatted_username)),
        FormTokenField(),
        SelectMenu(u'role', u'Role', options=role_options),
        SubmitButton(title=u'Submit', id_=u'submitbtn'))
    
    results = form(req, {u'role': membership.group_role})
    
    if results.successful:
        membership.group_role = results[u'role']
    
    return req.render_template('edit_group_member.mako',
        group=group,
        membership=membership,
        user=membership.user,
        form=results)

remove_member_form = Form(u'post', None,
    FormTokenField(),
    TextArea(u'reason', u'Reason',
             u'Plain text. This will be sent to the user being removed.'),
    SubmitButton(title=u'Remove', id_=u'remove'))

def remove_member(req, group_id, username):
    group, membership = _group_and_membership(group_id, username)
    req.check_group_permission(group, u'edit_members')
    if membership.user in (group.owner, req.user):
        return None
    
    results = remove_member_form(req)
    results.action = 'groups.remove_member', \
        dict(group_id=group.group_id, username=membership.user.unformatted_username)
    if results.successful:
        message_text = req.render_template_to_unicode('group_removal_mail_message.mako',
            group=group,
            membership=membership,
            remover=req.user,
            reason=render_plain_text(results[u'reason']))
        conversation = MailConversation(u'You have been removed from ' + group.name)
        participant = MailParticipant(conversation, membership.user, True)
        message = MailMessage(conversation, None, message_text)
        Session.save(conversation)
        Session.delete(membership)
        req.redirect('groups.group_members', group_id=group.group_id, removed=1)
    else:
        return req.render_template('remove_group_member.mako',
            group=group,
            membership=membership,
            form=results)

change_owner_form = Form(u'post', None,
    FormTokenField(),
    TextArea(u'reason', u'Reason',
             u"Plain text. This will be sent to the group's new owner."),
    SubmitButton(title=u'Change owner', id_=u'changeowner'))

def change_owner(req, group_id, username):
    group, membership = _group_and_membership(group_id, username)
    req.check_group_permission(group, None)
    if req.user != group.owner:
        raise Error403()
    if membership.user == group.owner:
        return None
    
    results = change_owner_form(req)
    results.action = 'groups.change_owner', \
        dict(group_id=group.group_id, username=membership.user.unformatted_username)
    if results.successful:
        message_text = req.render_template_to_unicode('group_owner_change_mail_message.mako',
            group=group,
            membership=membership,
            old_owner=req.user,
            reason=render_plain_text(results[u'reason']))
        conversation = MailConversation(u'You are the new owner of ' + group.name)
        participant = MailParticipant(conversation, membership.user, True)
        message = MailMessage(conversation, None, message_text)
        Session.save(conversation)
        group.owner = membership.user
        req.redirect('groups.group_members', group_id=group.group_id, owner_changed=1)
    else:
        return req.render_template('change_group_owner.mako',
            group=group,
            membership=membership,
            form=results)

edit_group_form = Form(u'post', None,
    FormTokenField(),
    description_field,
    TextArea(u'home_page', u'Home page',
        u'HTML. Only shown to members.',
        rows=15,
        modifiers=[HtmlModifier()]),
    SubmitButton(title=u'Edit', id_=u'editbtn'))

def edit_group(req, group_id):
    group = Group.query.get(group_id)
    if group is None:
        return None
    req.check_group_permission(group, u'edit_group')
    
    results = edit_group_form(req, {
        u'description': group.description,
        u'home_page': (group.home_page, group.rendered_home_page)
    })
    results.action = 'groups.edit_group', dict(group_id=group.group_id)
    if results.successful:
        group.description = results[u'description']
        group.home_page, group.rendered_home_page = results[u'home_page']
    return req.render_template('edit_group.mako',
        group=group,
        form=results)

delete_group_form = Form(u'post', None,
    FormTokenField(),
    TextField(u'confirmation', u'Confirm',
              u'Type "DeLeTe" in alternating case as shown to confirm.',
              modifiers=[SpecificValueValidator(u'DeLeTe')]),
    SubmitButton(title=u'Delete', id_=u'deletebtn'))

def delete_group(req, group_id):
    group = Group.query.get(group_id)
    if group is None:
        return None
    req.check_group_permission(group, None)
    if req.user != group.owner:
        raise Error403()
    
    results = delete_group_form(req)
    results.action = 'groups.delete_group', dict(group_id=group.group_id)
    
    if results.successful:
        Session.delete(group)
        Session.flush()
        req.redirect('groups', deleted=1)
    else:
        return req.render_template('delete_group.mako',
            group=group,
            form=results)

def downgrade_group_type(req, group_id):
    group = Group.query.get(group_id)
    if group is None:
        return None
    req.check_group_permission(group, None)
    if req.user != group.owner:
        raise Error403()
    
    type_options = [
        (type_code, Group.type_names[type_code])
        for type_code in xrange(group.type-1, -1, -1)
    ]
    
    form = Form(u'post', None,
        FormTokenField(),
        SelectMenu(u'type', u'New type', options=type_options),
        SubmitButton(id_=u'submitbtn', title=u'Change'))
    results = form(req)
    
    if results.successful:
        group.type = results[u'type']
        req.redirect('groups.group', group_id=group.group_id, type_changed=1)
    else:
        return req.render_template('downgrade_group_type.mako',
            group=group,
            form=results)

def make_forum_form(group):
    permissions = group.special_permissions.order_by(
        desc(SpecialGroupPermission.special_group_permission_id)
    )
    permission_options = [(None, u'(No permission required)')]
    for permission in permissions:
        permission_options.append((permission, permission.title))
    
    
    return Form(u'post', None,
        FormTokenField(),
        TextField(u'name', u'Name', modifiers=[NotBlankValidator()]),
        SelectMenu(u'view_permission', u'View permission', options=permission_options),
        SelectMenu(u'create_post_permission', u'Create post permission', options=permission_options),
        SelectMenu(u'create_thread_permission', u'Create thread permission', options=permission_options),
        SubmitButton(title=u'Create', id_=u'createbtn')) 

def create_forum(req, group_id):
    group = Group.query.get(group_id)
    if group is None:
        return None
    req.check_group_permission(group, u'edit_forums')
    
    results = make_forum_form(group)(req)
    
    if results.successful:
        forum = Forum(results[u'name'], group)
        forum.view_group_permission = results[u'view_permission']
        forum.create_post_group_permission = results[u'create_post_permission']
        forum.create_thread_group_permission = results[u'create_thread_permission']
        Session.flush()
        req.redirect('forums.forum', forum_id=forum.forum_id)
    else:
        return req.render_template('create_group_forum.mako',
            group=group,
            form=results)

def edit_group_forum(req, forum):
    # This isn't a real page; it's a function that gets called by
    # forums.edit_forum when the forum to be edited is part of a group
    group = forum.group
    req.check_group_permission(group, u'edit_forums')
    
    defaults = {
        u'name': forum.name,
        u'view_permission': forum.view_group_permission,
        u'create_post_permission': forum.create_post_group_permission,
        u'create_thread_permission': forum.create_thread_group_permission
    }
    results = make_forum_form(group)(req, defaults)
    if results.successful:
        forum.name = results[u'name']
        forum.view_group_permission = results[u'view_permission']
        forum.create_post_group_permission = results[u'create_post_permission']
        forum.create_thread_group_permission = results[u'create_thread_permission']
        req.redirect('forums', group_id=group.group_id, edited=1)
    else:
        return req.render_template('edit_group_forum.mako',
            group=group,
            forum=forum,
            form=results)
    

def edit_roles(req, group_id):
    group = Group.query.get(group_id)
    if group is None:
        return None
    req.check_group_permission(group, u'edit_roles')
    
    # Showing and sorting by the number of members with the role would be nice,
    # but CountKeeperExtension isn't fancy enough to notice when the property
    # changes, which GroupMember.role sometimes does.
    roles = group.roles.order_by(GroupRole.name).all()
    
    return req.render_template('edit_group_roles.mako',
        group=group,
        roles=roles)

def make_role_form(group, btntext):
    # Unnecessary personal trivia: I'm coding this from my roof. It's sunny,
    # and birds are chirping. This rules!
    standard_permission_options = [
        (permission, permission.title, permission.description)
        for permission in StandardGroupPermission.query.order_by(StandardGroupPermission.title)
    ]
    special_permission_options = [
        (permission, permission.title)
        for permission in group.special_permissions.order_by(SpecialGroupPermission.title)
    ]
    return Form(u'post', None,
        FormTokenField(),
        TextField(u'name', u'Name', modifiers=[NotBlankValidator()]),
        CheckBoxes(u'standard_permissions', u'Standard permissions',
                   options=standard_permission_options),
        CheckBoxes(u'special_permissions', u'Special permissions',
                   options=special_permission_options),
        SubmitButton(id_=u'submitbtn', title=btntext),
        reliable_field=u'form_token')

def create_role(req, group_id):
    group = Group.query.get(group_id)
    if group is None:
        return None
    req.check_group_permission(group, u'edit_roles')
    
    results = make_role_form(group, u'Create')(req)
    if results.successful:
        role = GroupRole(group, results[u'name'])
        for standard_permission in results[u'standard_permissions']:
            role.standard_permissions.append(standard_permission)
        for special_permission in results[u'special_permissions']:
            role.special_permissions.append(special_permission)
        req.redirect('groups.edit_roles', group_id=group_id, created=1)
    else:
        return req.render_template('create_group_role.mako',
            group=group,
            form=results)

def edit_role(req, role_id):
    role = GroupRole.query.get(role_id)
    if role is None:
        return None
    group = role.group
    req.check_group_permission(group, u'edit_roles')
    
    results = make_role_form(group, u'Edit')(req, {
        u'name': role.name,
        u'standard_permissions': role.standard_permissions,
        u'special_permissions': role.special_permissions
    })
    if results.successful:
        role.name = results[u'name']
        role.standard_permissions = results[u'standard_permissions']
        role.special_permissions = results[u'special_permissions']
        req.redirect('groups.edit_roles', group_id=group.group_id, edited=1)
    else:
        return req.render_template('edit_group_role.mako',
            group=group,
            role=role,
            form=results)

def delete_role(req, role_id):
    role = GroupRole.query.get(role_id)
    if role is None:
        return None
    group = role.group
    req.check_group_permission(group, u'edit_roles')
    
    if role.members[:1].count():
        return req.render_template('cant_delete_group_role.mako',
            group=group,
            role=role)
    
    confirm(u'delete that role')
    
    Session.delete(role)
    req.redirect('groups.edit_roles', group_id=group.group_id, deleted=1)

def make_role_default(req, role_id):
    role = GroupRole.query.get(role_id)
    if role is None:
        return None
    group = role.group
    req.check_group_permission(group, u'edit_roles')
    
    confirm(u'make that role the default')
    
    group.default_role = role
    req.redirect('groups.edit_roles', group_id=group.group_id, made_default=1)

# I'm not going to lie, Rails' scaffolding has its advantages

def edit_special_permissions(req, group_id):
    group = Group.query.get(group_id)
    if group is None:
        return None
    req.check_group_permission(group, u'edit_special_permissions')
    
    permissions = group.special_permissions.order_by(SpecialGroupPermission.title).all()
    
    return req.render_template('edit_special_permissions.mako',
        group=group,
        permissions=permissions)

special_permission_form = Form(u'post', None, # Holy crap! I'm reusing something?!
    FormTokenField(),
    TextField(u'name', u'Name', modifiers=[NotBlankValidator()]),
    SubmitButton(title=u'Create', id_=u'createbtn')
)

def create_special_permission(req, group_id):
    group = Group.query.get(group_id)
    if group is None:
        return None
    req.check_group_permission(group, u'edit_special_permissions')
    
    results = special_permission_form(req)
    results.action = 'groups.create_special_permission', dict(group_id=group.group_id)
    if results.successful:
        permission = SpecialGroupPermission(group, results[u'name'])
        Session.save(permission)
        req.redirect('groups.edit_special_permissions', group_id=group.group_id, created=1)
    else:
        return req.render_template('create_special_permission.mako',
            group=group,
            form=results)

def edit_special_permission(req, permission_id):
    permission = SpecialGroupPermission.query.get(permission_id)
    if permission is None:
        return None
    group = permission.group
    req.check_group_permission(group, u'edit_special_permissions')
    
    results = special_permission_form(req, {u'name': permission.title})
    results.action = 'groups.edit_special_permission', dict(permission_id=permission.special_group_permission_id)
    if results.successful:
        permission.title = results[u'name']
        req.redirect('groups.edit_special_permissions', group_id=group.group_id, edited=1)
    else:
        return req.render_template('edit_special_permission.mako',
            group=group,
            permission=permission,
            form=results)

def delete_special_permission(req, permission_id):
    permission = SpecialGroupPermission.query.get(permission_id)
    if permission is None:
        return None
    group = permission.group
    req.check_group_permission(group, u'edit_special_permissions')
    
    confirm('delete this permission')
    Session.delete(permission)
    req.redirect('groups.edit_special_permissions', group_id=group.group_id, deleted=1)