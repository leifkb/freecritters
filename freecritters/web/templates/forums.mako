<%inherit file="maybe_group_layout.mako"/>\
<%def name="title()">\
% if group is not None:
${group.name} \
% endif
Forums</%def>\

% if not forums:
<p>No forums found.</p>
% else:
<table class="normal">
    <thead>
        <tr>
            <th>Forum</th>
            <th>Threads</th>
        </tr>
    </thead>
    <tbody>
        % for forum in forums:
        % if fc.req.has_permission_and_group_permission(forum.group, forum.view_permission, forum.view_group_permission):
        <tr>
            <td class="forumnamecol dedicatedtolink"><a href="${fc.url('forums.forum', forum_id=forum.forum_id)}">${forum.name}</a></td>
            <td class="forumthreadcountcol">${forum.thread_count}</td>
        </tr>
        % endif
        % endfor
    </tbody>
</table>
% endif