<%inherit file="group_special_permissions_layout.mako"/>\
<%namespace file="formsuccess.mako" import="formsuccess"/>\
<%def name="title()">Editing group special permissions</%def>\

${formsuccess(
    created=u'Permission created.',
    edited=u'Permission edited.',
    deleted=u'Permission deleted.'
)}

<p>Special group permissions are permissions which you can create, specific to this group.
Forums can be set to require them for various actions.</p>
<p>To give a user access to a forum which requires a special permission, check that
permission off in the user's role.</p>

% if permissions:
<table class="normal">
    <thead>
        <th>Name</th>
        <th>Options</th>
    </thead>
    <tbody>
        % for permission in permissions:
        <tr>
            <td>${permission.title}</td>
            <td>
                <a href="${fc.url('groups.edit_special_permission', permission_id=permission.special_group_permission_id)}">(edit)</a>
                <a href="${fc.url('groups.delete_special_permission', permission_id=permission.special_group_permission_id)}" class="confirm">(delete)</a>
            </td>
        </tr>
        % endfor
    </tbody>
<thead>
% endif