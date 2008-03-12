<%inherit file="group_layout.mako"/>\
<%namespace file="formsuccess.mako" import="formsuccess"/>\
<%namespace file="paginator.mako" import="render_paginator_in_box"/>\
<%def name="title()">Members of ${group.name}</%def>

${formsuccess(
    removed=u'Member removed.',
    owner_changed=u'Owner changed.'
)}

<% can_edit = fc.req.has_group_permission(group, u'edit_members') %>\
<table class="normal" id="groupmembers">
    <thead>
        <tr>
            % if can_edit:
            <th>Edit</th>
            % endif
            <th>Member</th>
            <th>Role</th>
            <th>Joined</th>
        </tr>
    </thead>
    <tbody>
        % for member in members:
        <tr>
            % if can_edit:
            <td class="dedicatedtolink groupmemberseditcol"><div><a href="${fc.url('groups.edit_member', group_id=group.group_id, username=member.user.unformatted_username)}">Edit</a></div>
                % if member.user not in (group.owner, fc.req.user):
                <div><a href="${fc.url('groups.remove_member', group_id=group.group_id, username=member.user.unformatted_username)}">Remove</div>
                % endif
            </td>
            % endif
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