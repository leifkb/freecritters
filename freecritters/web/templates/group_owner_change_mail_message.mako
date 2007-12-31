<p>You have been made new owner of the group <a href="${fc.url('groups.group', group_id=group.group_id)}">${group.name}</a> by <a href="${fc.url('profile', username=old_owner.unformatted_username)}">${old_owner.username}</a>, its old owner.</p>

% if reason and not reason.isspace():
<p>The following reason was given:</p>

${reason|n}
% else:
<p>No reason was given.</p>
% endif