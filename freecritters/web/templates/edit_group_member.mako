<%inherit file="group_layout.mako"/>\
<%namespace file="form.mako" import="render_form"/>\
<%def name="title()">Editing group member: ${user.username}</%def>\

% if user != group.owner and user != fc.req.user:
<p><a href="${fc.url('groups.remove_member', group_id=group.group_id, username=user.unformatted_username)}">Remove</a>
% if fc.req.user == group.owner:
or <a href="${fc.url('groups.change_owner', group_id=group.group_id, username=user.unformatted_username)}">make new owner</a>
% endif
</p>
% endif

${render_form(form)}