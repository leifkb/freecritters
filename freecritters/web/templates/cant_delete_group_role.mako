<%inherit file="group_roles_layout.mako"/>\
<%def name="title()">Can't delete group role</%def>\

<p>You can't delete the role <strong>${role.name}</strong> because it is assigned to members.</p>