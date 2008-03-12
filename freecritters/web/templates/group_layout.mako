<%inherit file="layout.mako"/>\
<%def name="secondarynav()">\
<div class="nav">
    <h2>${group.type_name}: ${group.name}</h2>
    <ul>
        <li><a href="${fc.url('groups.group', group_id=group.group_id)}">Home</a></li>
        <li><a href="${fc.url('groups.leave_group', group_id=group.group_id)}" class="confirm">Leave</a></li>
        <li><a href="${fc.url('groups.group_members', group_id=group.group_id)}">Members</a></li>
        <li><a href="${fc.url('forums', group_id=group.group_id)}">Forums</a></li>
        % if fc.req.has_group_permission(group, u'edit_group'):
        <li><a href="${fc.url('groups.edit_group', group_id=group.group_id)}">Edit group</a></li>
        % endif
        % if fc.req.has_group_permission(group, u'edit_forums'):
        <li><a href="${fc.url('groups.create_forum', group_id=group.group_id)}">Add forum</a></li>
        % endif
        % if fc.req.has_group_permission(group, u'edit_roles'):
        <li><a href="${fc.url('groups.edit_roles', group_id=group.group_id)}">Edit roles</a></li>
        % endif
        % if fc.req.has_group_permission(group, u'edit_special_permissions'):
        <li><a href="${fc.url('groups.edit_special_permissions', group_id=group.group_id)}">Edit permissions</a></li>
        % endif
    </ul>
</div>\
</%def>\
${next.body()}