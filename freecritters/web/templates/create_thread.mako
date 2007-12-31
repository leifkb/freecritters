<%inherit file="forum_layout.mako"/>\
<%namespace file="form.mako" import="render_form"/>\
<%def name="title()">Creating thread on ${forum.name}</%def>\

% if preview is not None:
<div class="preview">
    <h3 class="previewtitle">Preview</h3>
    ${preview|n}
</div>
% endif

${render_form(form)}