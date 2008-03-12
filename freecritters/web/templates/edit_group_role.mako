<%inherit file="group_roles_layout.mako"/>\
<%namespace file="form.mako" import="render_form"/>\
<%def name="title()">Editing group role: ${role.name}</%def>\

${render_form(form)}