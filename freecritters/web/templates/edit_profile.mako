<%inherit file="settings_layout.mako"/>\
<%namespace file="form.mako" import="render_form"/>
<%def name="title()">Edit profile</%def>\

% if updated:
<p class="formsuccessful">Profile updated sucessfully.</p>
% endif
${render_form(form)}