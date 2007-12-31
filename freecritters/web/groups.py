# -*- coding: utf-8 -*-

from freecritters.web.form import \
    Form, SelectMenu, TextField, TextArea, HiddenField, SubmitButton, \
    LengthValidator, RegexValidator, SpecificValueValidator, NotBlankValidator
from sqlalchemy import asc, desc
from sqlalchemy.orm import eagerload
from freecritters.model import Session, User, Group, GroupMember, GroupRole, \
                               MailConversation, MailParticipant, MailMessage, \
                               Forum, SpecialGroupPermission
from freecritters.web.paginator import Paginator
from freecritters.web.modifiers import \
    FormTokenField, GroupNameNotTakenValidator, GroupTypeCompatibilityValidator, \
    HtmlModifier
from freecritters.web.globals import fc
from freecritters.textformats import render_plain_text
from freecritters.web.exceptions import Error403, Error404

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
    SelectMenu(u'type', u'Type', options=list((unicode(i), name) for i, name in enumerate(Group.type_names)),
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
        group = Group(int(results[u'type']), results[u'name'], results[u'description'], req.user)
        Session.save(group)
        Session.flush()
        req.redirect('groups.group', group_id=group.group_id)
    else:
        return req.render_template('create_group_form.mako',
            form=results)

def groups(req):
    req.check_permission(u'groups')
    
    groups = [
        membership.group
        for membership in req.user.group_memberships.join('group').order_by([
            desc(Group.owner_user_id==req.user.user_id),
            desc(Group.type),
            Group.unformatted_name
        ]).options(eagerload('group'))
    ]
    
    return req.render_template('groups.mako',
        groups=groups,
        left='left' in req.args,
        deleted='deleted' in req.args)

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

leave_group_form = Form(u'post', None,
    FormTokenField(),
    SubmitButton(title=u'Yes, leave it', id_=u'submit'))

def leave_group(req, group_id):
    group = Group.query.get(group_id)
    if group is None:
        return None
    req.check_group_permission(group, None)
    
    if req.user == group.owner:
        return req.render_template('leave_group_form.mako',
            group=group,
            is_owner=True)
        
    results = leave_group_form(req)
    results.action = 'groups.leave_group', dict(group_id=group.group_id)
    if results.successful:
        membership = req.user.find_group_membership(group)
        Session.delete(membership)
        req.redirect('groups', left=1)
    else:
        return req.render_template('leave_group_form.mako',
            is_owner=False,
            group=group,
            form=results)

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
        removed='removed' in req.args,
        owner_changed='owner_changed' in req.args,
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
        (unicode(role.group_role_id), role.name)
        for role in group.roles.order_by(GroupRole.name)
    )
    
    form = Form(u'post', ('groups.edit_member', dict(group_id=group.group_id, username=membership.user.username)),
        FormTokenField(),
        SelectMenu(u'role', u'Role', options=role_options),
        SubmitButton(title=u'Submit', id_=u'submitbtn'))
    
    results = form(req, {u'role': unicode(membership.group_role.group_role_id)})
    
    if results.successful:
        membership.group_role = GroupRole.query.get(int(results[u'role']))
    
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

def create_forum(req, group_id):
    group = Group.query.get(group_id)
    if group is None:
        return None
    req.check_group_permission(group, u'edit_forums')
    
    permissions = group.special_permissions.order_by(
        desc(SpecialGroupPermission.special_group_permission_id)
    )
    permission_options = [(u'', u'(No permission required)')]
    for permission in permissions:
        permissions_options.append((unicode(permission.permission_id), permission.name))
    
    
    form = Form(u'post', ('groups.create_forum', dict(group_id=group.group_id)),
        FormTokenField(),
        TextField(u'name', u'Name', modifiers=[NotBlankValidator()]),
        SelectMenu(u'view_permission', u'View permission', options=permission_options),
        SelectMenu(u'create_post_permission', u'Create post permission', options=permission_options),
        SelectMenu(u'create_thread_permission', u'Create thread permission', options=permission_options),
        SubmitButton(title=u'Create', id_=u'createbtn'))
    
    results = form(req, {u'view_permission': u'',
                         u'create_post_permission': u'',
                         u'create_thread_permission': u''})
    
    if results.successful:
        forum = Forum(results[u'name'], group)
        if results[u'view_permission']:
            forum.view_group_permission = SpecialGroupPermission.query.get(int(results[u'view_permission']))
        if results[u'create_post_permission']:
            forum.create_post_group_permission = SpecialGroupPermission.query.get(int(results[u'create_post_permission']))
        if results[u'create_thread_permission']:
            forum.create_thread_group_permission = SpecialGroupPermission.query.get(int(results[u'create_thread_permission']))
        Session.flush()
        req.redirect('forums.forum', forum_id=forum.forum_id)
    else:
        return req.render_template('create_group_forum.mako',
            group=group,
            form=results)