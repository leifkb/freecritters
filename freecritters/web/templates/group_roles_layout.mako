<%inherit file="group_layout.mako"/>\
<%def name="tabs()"><%
    return [
        Tab('Edit roles', 'groups.edit_roles', group_id=group.group_id),
        Tab('Create', 'groups.create_role', group_id=group.group_id)
    ]
%></%def>\
${next.body()}