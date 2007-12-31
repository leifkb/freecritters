<%inherit file="group_layout.mako"/>\
<%namespace file="form.mako" import="render_form"/>\
<%def name="title()">Making ${membership.user.username} owner of group</%def>\

<p>You are making <a href="${fc.url('profile', username=membership.user.unformatted_username)}">${membership.user.username}</a> the new owner of your group, ${group.name}. This will make him or her all-powerful in the group. You will continue to have your current role of ${fc.req.user.find_group_membership(group).group_role.name} in the group.</p>

${render_form(form)}