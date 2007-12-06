<%inherit file="settings_layout.mako"/>\
<%namespace file="form.mako" import="render_form"/>\
<%def name="title()">Editing subaccount: ${subaccount.name}</%def>\

% if updated:
<p class="formsuccessful">Subaccount edited successfully.</p>
% endif
${render_form(form)}