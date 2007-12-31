<%inherit file="group_layout.mako"/>\
<%namespace file="form.mako" import="render_form"/>\
<%def name="title()">Removing group member: ${membership.user.username}</%def>\

${render_form(form)}