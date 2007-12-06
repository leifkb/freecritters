<%inherit file="settings_layout.mako"/>\
<%def name="title()">Subaccounts</%def>\

% if deleted:
<p class="formsuccessful">Subaccount deleted.</p>
% endif
% if password_changed:
<p class="formsuccessful">Subaccount password changed.</p>
% endif
% if created:
<p class="formsuccessful">Subaccount created</p>
% endif

<p>Subaccounts allow you to create multiple passwords for logging into your
account with limited capabilities. This is useful if, for instance, you want
to let a friend take care of your pets while you're away, but you don't want
them to be able to read your mail or anything else.</p>

% if subaccounts:
<ul>
    % for subaccount in subaccounts:
    <li>${subaccount.name} <a href="${fc.url('settings.edit_subaccount', subaccount_id=subaccount.subaccount_id)}">(edit)</a> <a href="${fc.url('settings.change_subaccount_password', subaccount_id=subaccount.subaccount_id)}">(change password)</a> <a href="${fc.url('settings.delete_subaccount', subaccount_id=subaccount.subaccount_id)}">(delete)</a></li>
    % endfor
</ul>
% endif