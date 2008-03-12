<%inherit file="layout.mako"/>\
<%namespace file="form.mako" import="render_form"/>\
<%def name="title()">Are you sure?</%def>\

<p>Are you sure you want to ${action}? (If not, just go to another page.)</p>

${render_form(form)}