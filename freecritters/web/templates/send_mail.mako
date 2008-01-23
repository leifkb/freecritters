<%inherit file="mail_layout.mako"/>\
<%namespace file="form.mako" import="render_form"/>\
<%def name="title()">Send mail</%def>\
<%def name="head()">
<script src="${fc.url('static', fn='mailsend.js')}" type="text/javascript"></script>
</%def>\

<div id="premailmessagecontainer">
% if user is not None and user.rendered_pre_mail_message is not None:
<div class="premailmessage"><h3>${user.username} says:</h3>${user.rendered_pre_mail_message|n}</div>
% endif
</div>

% if preview is not None:
<div class="preview">
<h3 class="previewtitle">Preview</h3>
${preview|n}
</div>
% endif

${render_form(form)}