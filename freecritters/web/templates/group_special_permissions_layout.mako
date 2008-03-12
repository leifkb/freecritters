<%inherit file="group_layout.mako"/>\
<%def name="tabs()"><%
    return [
        Tab('Edit special permissions', 'groups.edit_special_permissions', group_id=group.group_id),
        Tab('Create', 'groups.create_special_permission', group_id=group.group_id)
    ]
%></%def>\
${next.body()}