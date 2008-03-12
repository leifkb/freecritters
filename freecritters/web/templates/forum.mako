<%inherit file="forum_layout.mako"/>\
<%namespace file="formsuccess.mako" import="formsuccess"/>\
<%namespace file="paginator.mako" import="render_paginator_in_box"/>\
<%def name="title()">Forum: ${forum.name}</%def>\

${formsuccess(thread_deleted=u'Thread deleted.')}

% if not threads:
<p>This forum is empty.</p>
% else:
<table class="normal forumthreads">
    <thead>
        <tr>
            <th class="threadsubjectcol">Subject</th>
            <th class="threadlastpostcol">Last post</th>
            <th class="threadpostscol">Posts</th>
            <th class="threadauthorcol">Author</th>
        </tr>
    </thead>
    <tbody>
        % for thread in threads:
        <tr>
            <td class="threadsubjectcol dedicatedtolink"><a href="${fc.url('forums.thread', thread_id=thread.thread_id)}">${thread.subject}</a></td>
            <td class="threadlastpostcol">\
            % if thread.last_post is not None:
            ${datetime(thread.last_post)}\
            % else:
            <em>never</em>\
            % endif
            </td>
            <td class="threadpostscol">${thread.post_count}</td>
            <td class="threadusercol dedicatedtolink"><a href="${fc.url('profile', username=thread.user.unformatted_username)}">${thread.user.username}</a></td>
        </tr>
        % endfor
    </tbody>
</table>
${render_paginator_in_box(paginator)}
% endif