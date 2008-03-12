<%inherit file="group_special_permissions_layout.mako"/>\
<%def name="title()">Editing special group permission: ${permission.title}</%def>\
<%namespace file="form.mako" import="*"/>\

${render_form(form)}