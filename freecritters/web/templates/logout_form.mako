<%inherit file="layout.mako"/>\
<%namespace file="form.mako" import="render_form"/>\
<%def name="title()">Log out</%def>\
<p>Are you sure you want to log out? (If not, just go to another page.)</p>
${render_form(form)}