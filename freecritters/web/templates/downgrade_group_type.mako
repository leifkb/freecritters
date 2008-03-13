<%inherit file="group_layout.mako"/>\
<%namespace file="form.mako" import="render_form"/>\
<% from freecritters.model.group import Group %>\
<%def name="title()">Changing group type</%def>\

<p>Your group is currently a ${group.type_name}. \
% if group.type == 0:
Group types can only be made less restrictive, and there is no type of group less restrictive than a ${group.type_name}. You can not change your group's type.</p>
% else:
% if group.type == 1:
Group types can only be made less restrictive, and there is one type of group less restrictive than a ${group.type_name}. You can turn your group into a ${Group.type_names[group.type-1]} if you would like.
% elif group.type == 2:
Group types can only be made less restrictive, and there are two types of group less restrictive than a ${group.type_name}. You can turn your group into a ${Group.types_names[group.type-1]} or a ${Group.type_names[group.type-2]} if you would like.
% endif
</p>
<p>Note that this action <strong>can not be undone</strong>: because group types can only be made less restrictive, you will <strong>never be able</strong> to turn your group back into a ${group.type_name} if you change it now.<p>
${render_form(form)}
% endif