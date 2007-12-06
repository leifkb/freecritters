<%inherit file="mail_layout.mako"/>\
<%namespace file="form.mako" import="render_form"/>\
<%def name="title()">Reply to mail</%def>\

% if preview is not None:
<div class="preview">
<h3 class="previewtitle">Preview</h3>
${preview|n}
</div>
% endif

${render_form(reply_form)}
