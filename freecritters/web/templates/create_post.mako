<%inherit file="forum_layout.mako"/>\
<%namespace file="form.mako" import="render_form"/>\
<%def name="title()">Posting</%def>\

<p>Posting to <a href="${fc.url('forums.thread', thread_id=thread.thread_id)}">${thread.subject}</a>.</p>

% if preview is not None:
<div class="preview">
    <h3 class="previewtitle">Preview</h3>
    ${preview|n}
</div>
% endif

${render_form(form)}