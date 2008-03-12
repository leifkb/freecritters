<%def name="render_paginator(paginator)">
<form action="${paginator.path}" method="get" class="paginatorform">
<div class="paginator">
% for name, value in paginator.args:
<input type="hidden" name="${name}" value="${value}">
% endfor
% if paginator.page > 1:
<a href="${paginator.page_url(1)}">first</a>
<a href="${paginator.page_url(paginator.page-1)}">previous</a>
% endif
Page <input type="text" name="${paginator.paginator.argument}" size="${len(str(paginator.page_count))}" maxlength="${len(str(paginator.page_count))}" value="${paginator.page}"> of ${paginator.page_count}
<input type="submit" value="Go">
% if paginator.page < paginator.page_count:
<a href="${paginator.page_url(paginator.page+1)}">next</a>
<a href="${paginator.page_url(paginator.page_count)}">last</a>
% endif
</div>
</form>
</%def>

<%def name="render_paginator_in_box(paginator, left_aligned=False, always_show=False)">
% if always_show or paginator.page_count > 1:
<div class="paginatorcontainer\
% if left_aligned:
left\
% endif
">
${render_paginator(paginator)}
</div>
% endif
</%def>