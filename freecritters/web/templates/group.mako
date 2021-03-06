<%inherit file="${fc.is_member and 'group_layout.mako' or 'layout.mako'}" />\
<%namespace file="form.mako" import="render_form"/>\
<%namespace file="formsuccess.mako" import="formsuccess"/>\
<%def name="title()">${group.type_name}: ${group.name}</%def>\

${formsuccess(type_changed=u'Group type changed.')}

<table class="labels">
    <tbody>
        <tr>
            <th>Owner:</th>
            <td class="dedicatedtolink"><a href="${fc.url('profile', username=group.owner.unformatted_username)}">${group.owner.username}</a></td>
        </tr>
        <tr>
            <th>Created:</th>
            <td>${datetime(group.created)}</td>
        </tr>
        <tr>
            <th>Members:</th>
            <td>${group.member_count}</td>
        </tr>
        <tr>
            <th>Description:</th>
            <td>${group.rendered_description|n}</td>
        </tr>
    </tbody>
</table>

% if join_form is not None:
${render_form(join_form)}
% endif

% if is_member:
${group.rendered_home_page|n}
% endif