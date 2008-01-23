<%inherit file="forum_layout.mako"/>\
<%namespace file="form.mako" import="render_form"/>\
<%def name="title()">Deleting post</%def>\

<p>Are you sure you want to delete this post? (If not, just go to another page.</p>
${render_form(form)}