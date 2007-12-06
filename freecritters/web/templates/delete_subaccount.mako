<%inherit file="settings_layout.mako"/>\
<%namespace file="form.mako" import="render_form"/>\
<%def name="title()">Delete subaccount: ${subaccount.name}</%def>\

<p>Are you sure you want to delete this subaccount? (If not, just go to another page.)</p>
${render_form(form)}