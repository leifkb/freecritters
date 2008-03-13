<%inherit file="group_layout.mako"/>\
<%namespace file="form.mako" import="render_form"/>\
<%def name="title()">Editing group</%def>\

% if fc.req.user == group.owner:
<p><a href="${fc.url('groups.delete_group', group_id=group.group_id)}">Delete group</a>, <a href="${fc.url('groups.downgrade_group_type', group_id=group.group_id)}">change group type</a></p>
% endif

% if form.successful:
<p class="formsuccessful">Edited successfully.</p>
% endif

${render_form(form)}