# -*- coding: utf-8 -*-

from freecritters.web.form import Form, SelectMenu, SubmitButton
from storm.locals import Asc, Desc
from freecritters.model import Group
from freecritters.web.paginator import Paginator

def groups(req):
    req.check_permission(u'groups')
    return req.render_template('groups.html')

orders = {
    u'members': Desc(Group.member_count),
#    u'newest': Desc(Group.created),
#    u'oldest': Asc(Group.created)
}

order_names = [
    (u'members', u'Most members'),
#    (u'newest', u'Newest'),
#    (u'oldest', u'Oldest')
]

class GroupListSortForm(Form):
    method = u'get'
    action = u'/groups/list'
    field_prefix = u'sort'
    fields = [
        SelectMenu(u'order', u'Sort by', options=order_names),
        SubmitButton(title=u'Sort', id_=u'submit')
    ]

def _group_data(group, highest_group_type):
    return {
        u'name': group.name,
        u'description': group.rendered_description,
        u'member_count': group.member_count,
        u'created': group.created,
        u'acceptable_type': acceptable_type,
        u'type': group.can_coexist_with(highest_group_type)
    }

def group_list(req):
    req.check_permission(u'groups')
    sort_form = GroupListSortForm(req, {u'order': u'members'})
    order = orders[sort_form.values_dict()[u'order']]
    paginator = Paginator(req, Group.find().count())
    highest_group_type = req.user.groups.find().max(Group.type)
    groups = [_group_data(group, highest_group_type)
              for group in paginator(Group.find().order_by(order))]
    return req.render_template('group_list.html',
        groups=groups,
        sort_form=sort_form.generate(),
        paginator=paginator
    )