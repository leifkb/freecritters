<%inherit file="group_special_permissions_layout.mako"/>\
<%namespace file="form.mako" import="render_form"/>\
<%def name="title()">Deleting special permission: ${permission.name}</%def>\

<p>Are you sure you want to delete this permission? (If not, go to a different page.)</p>
${render_form(form)}