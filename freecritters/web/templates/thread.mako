<%inherit file="forum_layout.mako"/>\
<%namespace file="formsuccess.mako" import="formsuccess"/>\
<%namespace file="paginator.mako" import="render_paginator_in_box"/>\
<%namespace file="form.mako" import="render_form"/>\
<%! from simplejson import dumps %>\
<%def name="title()">Thread: ${thread.subject}</%def>\

${formsuccess(post_deleted=u'Post deleted.')}

<% can_delete = fc.req.has_named_permission(group, u'moderate') %>\

% if can_delete:
<p><a href="${fc.url('forums.delete_thread', thread_id=thread.thread_id)}" class="confirm">Delete</a></p>
% endif

% if not posts:
<p>No posts in this thread.</p>
% else:
${render_paginator_in_box(paginator)}
<table class="threadposts normal">
    <thead>
        <tr>
            <th>Meta</th>
            <th>Message</th>
        </tr>
    </thead>
    <tbody>
        % for post in posts:
        <tr class="postrow" id="post${post.post_id}">
            <td class="postmetacol">
                <div class="postauthor"><strong><a href="${fc.url('profile', username=post.user.unformatted_username)}">${post.user.username}</a></strong></div>
                <div class="postauthorrole">${post.user.role.name}</div>
                % if post.membership is not None:
                <div class="postauthorgrouprole">${post.membership.group_role.name}</div>
                % endif
                <div class="postcreated">${datetime(post.created, u'<br>')|n}</div>
                % if form:
                <div><a href="${fc.url('forums.thread', thread_id=thread.thread_id, quote=post.post_id)}#message" onclick="quote('message', ${dumps(post.message)}); return false;">Quote</a></div>
                % endif
                % if can_delete:
                <div><a href="${fc.url('forums.delete_post', post_id=post.post_id)}" class="confirm">Delete</a></div>
                % endif
            </td>
            <td class="postmessagecol">${post.rendered_message|n}</td>
        </tr>
        % endfor
    </tbody>
</table>
${render_paginator_in_box(paginator)}
% endif

% if form:
<h2 id="createpost">Post</h2>
${render_form(form)}
% endif