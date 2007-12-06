<%inherit file="layout.mako"/>\

<div id="groupmenu">
    <h3>${group.type_name}: ${group.name}</h3>
    <ul>
        <li><a href="${fc.url('groups.group', group_id=group.group_id)}">Home</a></li>
        <li><a href="${fc.url('groups.leave_group', group_id=group.group_id)}">Leave</a></li>
        <li><a href="${fc.url('groups.group_members', group_id=group.group_id)}">Members</a></li>
    </ul>
</div>
<div id="groupcontent">
    ${next.body()}
</div>