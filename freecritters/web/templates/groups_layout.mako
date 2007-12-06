<%inherit file="layout.mako"/>\
<%def name="tabs()"><%
    return [
        Tab('Groups', 'groups'),
        Tab('List', 'groups.group_list'),
        Tab('Create', 'groups.create_group')
    ]
%></%def>\
${next.body()}