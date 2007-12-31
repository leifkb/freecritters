<p>You have been removed from the group <a href="${fc.url('groups.group', group_id=group.group_id)}">${group.name}</a> by <a href="${fc.url('profile', username=remover.unformatted_username)}">${remover.username}</a>.</p>

% if reason and not reason.isspace():
<p>The following reason was given:</p>

${reason|n}
% else:
<p>No reason was given.</p>
% endif