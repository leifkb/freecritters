<%inherit file="group_roles_layout.mako"/>\
<%namespace file="formsuccess.mako" import="formsuccess"/>\
<%def name="title()">Editing group roles</%def>\

${formsuccess(
    created=u'Role created.',
    edited=u'Role edited.',
    deleted=u'Role deleted.',
    made_default=u'Role made default.'
)}

<p>Members in a group have a <strong>role</strong>, which determines what their job in the group is, and what they are capable of doing. You can alter the permissions assigned to existing roles here, or create new roles. You can also make a role the default which is assigned to newly-joining members.</p>

<table class="normal">
    <thead>
        <tr>
            <th>Name</th>
            <th>Options</th>
        </tr>
    </thead>
    <tbody>
        % for role in roles:
        <tr>
            <td>${role.name}</td>
            <td>
                <a href="${fc.url('groups.edit_role', role_id=role.group_role_id)}">(edit)</a>
                <a href="${fc.url('groups.delete_role', role_id=role.group_role_id)}" class="confirm">(delete)</a>
                % if role.is_default:
                <strong>default</strong>
                % else:
                <a href="${fc.url('groups.make_role_default', role_id=role.group_role_id)}" class="confirm">(make default)</a>
                % endif
        </tr>
        % endfor
    </tbody>
</table>