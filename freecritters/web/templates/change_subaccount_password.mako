<%inherit file="settings_layout.mako"/>\
<%namespace file="form.mako" import="render_form"/>\
<%def name="title()">Change subaccount password: ${subaccount.name}</%def>\

${render_form(form)}