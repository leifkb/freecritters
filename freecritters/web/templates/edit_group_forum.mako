<%inherit file="group_layout.mako"/>\
<%namespace file="form.mako" import="render_form"/>\
<%def name="title()">Editing group forum: ${forum.name}</%def>\

${render_form(form)}