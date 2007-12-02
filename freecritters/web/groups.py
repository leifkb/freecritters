# -*- coding: utf-8 -*-

from freecritters.web.form import \
    Form, SelectMenu, TextField, TextArea, HiddenField, SubmitButton, \
    LengthValidator, RegexValidator
from sqlalchemy import asc, desc
from sqlalchemy.orm import eagerload
from freecritters.model import Session, User, Group, GroupMember
from freecritters.web.paginator import Paginator
from freecritters.web.modifiers import \
    FormTokenField, GroupNameNotTakenValidator, GroupTypeCompatibilityValidator

class CreateGroupForm(Form):
    method = u'post'
    action = 'groups.create_group'
    fields = [
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
        TextArea(u'description', u'Description',
                 u'Plain text. Limited to %s characters.' % Group.max_description_length,
                 modifiers=[LengthValidator(25, Group.max_description_length)]),
        SubmitButton(title=u'Create', id_=u'createbtn')
    ]

def create_group(req):
    req.check_permission(u'groups')
    
    owned_group_count = Group.query.filter_by(owner_user_id=req.user.user_id).count()
    max_ownable_count = req.config.groups.ownable_per_user
    if max_ownable_count is not None and owned_group_count >= max_ownable_count:
        return req.render_template('too_many_owned_groups.html',
            owned_group_count=owned_group_count,
            max_ownable_count=max_ownable_count)
    
    form = CreateGroupForm(req)
    if form.was_filled and not form.errors:
        values = form.values_dict()
        group = Group(int(values[u'type']), values[u'name'], values[u'description'], req.user)
        Session.save(group)
        Session.flush()
        req.redirect('groups.group', group_id=group.group_id)
    else:
        return req.render_template('create_group_form.html',
            form=form.generate())

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
    
    return req.render_template('groups.html',
        groups=groups,
        left='left' in req.args)

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

class GroupListSortForm(Form):
    method = u'get'
    action = 'groups.group_list'
    field_prefix = u'sort'
    fields = [
        SelectMenu(u'order', u'Sort by', options=order_names),
        SubmitButton(title=u'Sort', id_=u'submit')
    ]

group_list_paginator = Paginator(15)

def group_list(req):
    req.check_permission(u'groups')
    
    sort_form = GroupListSortForm(req, {u'order': u'members'})
    order = orders[sort_form.values_dict()[u'order']]
    
    groups = Group.query.order_by(order)
    paginated = group_list_paginator(req, groups)

    return req.render_template('group_list.html',
        max_group_type=req.user.max_group_type,
        groups=paginated.all(),
        sort_form=sort_form.generate(),
        paginator=paginated
    )

class JoinForm(Form):
    method = u'post'
    fields = [
        FormTokenField(),
        SubmitButton(title=u'Join', id_=u'submit')
    ]

def group(req, group_id):
    group = Group.query.get(group_id)
    if group is None:
        return None
    req.check_permission(u'groups')
    membership = req.user.group_memberships.filter_by(group_id=group.group_id).first()
    if membership is None:
        is_member = False
        if group.can_coexist_with(req.user.max_group_type):
            join_form = JoinForm(req)
            join_form.action = 'groups.group', dict(group_id=group.group_id)
            if join_form.was_filled and not join_form.errors:
                membership = GroupMember(req.user, group, group.default_role)
                Session.save(membership)
                join_form = None
                is_member = True
            else:
                join_form = join_form.generate()
        else:
            join_form = None
    else:
        join_form = None
        is_member = True
        
    return req.render_template('group.html',
        group=group,
        is_member=is_member,
        join_form=join_form)

class LeaveGroupForm(Form):
    method = u'post'
    fields = [
        FormTokenField(),
        SubmitButton(title=u'Yes, leave it', id_=u'submit')
    ]

def leave_group(req, group_id):
    group = Group.query.get(group_id)
    if group is None:
        return None
    req.check_group_permission(group, None)
    
    if req.user == group.owner:
        return req.render_template('leave_group_form.html',
            group=group,
            is_owner=True)
        
    form = LeaveGroupForm(req)
    form.action = 'groups.leave_group', dict(group_id=group.group_id)
    if form.was_filled and not form.errors:
        membership = req.user.find_group_membership(group)
        Session.delete(membership)
        req.redirect('groups', left=1)
    else:
        return req.render_template('leave_group_form.html',
            is_owner=False,
            group=group,
            form=form.generate())

group_member_paginator = Paginator()

def group_members(req, group_id):
    group = Group.query.get(group_id)
    if group is None:
        return None
    req.check_group_permission(group, None)
    
    members = group.members.join('user').options(eagerload('user'), eagerload('role')).order_by([
        desc(User.user_id==group.owner_user_id),
        desc(GroupMember.joined)
    ])
    paginated = group_member_paginator(req, members)
    
    return req.render_template('group_members.html',
        group=group,
        paginator=paginated,
        members=paginated.all())