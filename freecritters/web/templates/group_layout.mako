<%inherit file="layout.mako"/>\
<%def name="secondarynav()">\
<div class="nav">
    <h2>${group.type_name}: ${group.name}</h2>
    <ul>
        <li><a href="${fc.url('groups.group', group_id=group.group_id)}">Home</a></li>
        <li><a href="${fc.url('groups.leave_group', group_id=group.group_id)}">Leave</a></li>
        <li><a href="${fc.url('groups.group_members', group_id=group.group_id)}">Members</a></li>
        <li><a href="${fc.url('forums', group_id=group.group_id)}">Forums</a></li>
        % if fc.req.has_group_permission(group, u'edit_group'):
        <li><a href="${fc.url('groups.edit_group', group_id=group.group_id)}">Edit group</a></li>
        % endif
    </ul>
</div>\
</%def>\
${next.body()}