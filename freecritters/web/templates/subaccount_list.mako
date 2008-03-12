<%inherit file="settings_layout.mako"/>\
<%namespace file="formsuccess.mako" import="formsuccess"/>\
<%def name="title()">Subaccounts</%def>\

${formsuccess(
    deleted=u'Subaccount deleted.',
    password_changed=u'Subaccount password changed.',
    created=u'Subaccount created.',
    edited=u'Subaccount edited.'
)}

<p>Subaccounts allow you to create multiple passwords for logging into your
account with limited capabilities. This is useful if, for instance, you want
to let a friend take care of your pets while you're away, but you don't want
them to be able to read your mail or anything else.</p>

% if subaccounts:
<table class="normal">
    <thead>
        <tr>
            <th>Name</th>
            <th>Options</th>
        </tr>
    </thead>
    <tbody>
    % for subaccount in subaccounts:
        <tr>
            <td>${subaccount.name}</td>
            <td>
                <a href="${fc.url('settings.edit_subaccount', subaccount_id=subaccount.subaccount_id)}">(edit)</a>
                <a href="${fc.url('settings.change_subaccount_password', subaccount_id=subaccount.subaccount_id)}">(change password)</a>
                <a href="${fc.url('settings.delete_subaccount', subaccount_id=subaccount.subaccount_id)}" class="confirm">(delete)</a>
            </td>
        </tr>
    % endfor
    </tbody>
</table>
% endif