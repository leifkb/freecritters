<%inherit file="layout.mako"/>\
<%namespace file="form.mako" import="render_form"/>\
<%def name="title()">Home</%def>\
<p>Home page-y stuff will go here.</p>
${render_form(form)}