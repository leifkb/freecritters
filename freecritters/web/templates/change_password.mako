<%inherit file="settings_layout.mako"/>\
<%namespace file="form.mako" import="render_form"/>\
<%def name="title()">Changing password</%def>\

% if changed:
<p class="formsuccessful">Password changed.</p>
% endif

${render_form(form)}