<%inherit file="group_layout.mako"/>\
<%namespace file="paginator.mako" import="render_paginator_in_box"/>\
<%def name="title()">Members of ${group.name}</%def>

<table class="normal" id="groupmembers">
    <thead>
        <tr>
            <th>Member</th>
            <th>Role</th>
            <th>Joined</th>
        </tr>
    </thead>
    <tbody>
        % for member in members:
        <tr>
            <td class="dedicatedtolink groupmembersusernamecol"><a href="${fc.url('profile', username=member.user.unformatted_username)}">${member.user.username}</a></td>
            <td class="groupmembersrolecol">
                ${member.group_role.name}
                % if member.user == group.owner:
                <strong>(owner)</strong>
                % endif
            </td>
            <td class="groupmembersjoinedcol">${datetime(member.joined)}</td>
        </tr>
        % endfor
    </tbody>
</table>
${render_paginator_in_box(paginator)}