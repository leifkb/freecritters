<%inherit file="group_layout.mako"/>\
<%namespace file="form.mako" import="render_form"/>\
<%def name="title()">Deleting ${group.name}</%def>\

<p>You are deleting your group, ${group.name}. If you proceed, the entire group &ndash; from its forums to its member list &ndash; will be lost.</p>

<p><strong>This action can not be undone.</strong></p>

${render_form(form)}