<%inherit file="groups_layout.mako"/>\
<%namespace file="form.mako" import="render_form_start_tag, render_form_field"/>\
<%namespace file="paginator.mako" import="render_paginator_in_box"/>\
<%def name="title()">Group list</%def>\

<div class="sortform">
    ${render_form_start_tag(sort_form)}
    <label for="${sort_form.form.id_prefix}${sort_form.form.field(u'order').id_}">Sort by:</label>
    ${render_form_field(sort_form.field_results(u'order'))}
    ${render_form_field(sort_form.field_results(u'submit'))}
    </form>
</div>

% if groups:
<table class="normal">
    <thead>
        <tr>
            <th>Group</th>
            <th>Type</th>
            <th>Members</th>
            <th>Owner</th>
            <th>Created</th>
        </tr>
    </thead>
    <tbody>
        % for group in groups:
<%      acceptable_type = group.can_coexist_with(max_group_type) %>
        <tr>
            <td class="groupgroupcol dedicatedtolink">
                <h3><a href="${fc.url('groups.group', group_id=group.group_id)}">${group.name}</a></h3>
                ${group.rendered_description|n}
            </td>
            <td class="grouptypecol">
                % if acceptable_type:
                <strong>
                % endif
                ${group.type_name}
                % if acceptable_type:
                </strong>
                % endif
            </td>
            <td class="groupmemberscol">${group.member_count}</td>
            <td class="groupownercol dedicatedtolink"><a href="${fc.url('profile', username=group.owner.unformatted_username)}">${group.owner.username}</a></td>
            <td class="groupcreatedcol">${datetime(group.created)}</td>
        </tr>
        % endfor
    </tbody>
</table>
% else:
<p>No groups found.</p>
% endif

${render_paginator_in_box(paginator)}