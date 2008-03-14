<%inherit file="maybe_group_layout.mako"/>\
<%namespace file="formsuccess.mako" import="formsuccess"/>\
<%def name="title()">\
% if group is not None:
${group.name} \
% endif
Forums</%def>\

${formsuccess(
    edited=u'Forum edited.',
    deleted=u'Forum deleted.'
)}

% if not forums:
<p>No forums found.</p>
% else:
<table class="normal">
    <thead>
        <tr>
            <th>Forum</th>
            <th>Threads</th>
            % if fc.req.has_named_permission(group, u'edit_forums'):
            <th>Options</th>
            % endif
        </tr>
    </thead>
    <tbody>
        % for forum in forums:
        % if fc.req.has_permission_and_group_permission(forum.group, forum.view_permission, forum.view_group_permission):
        <tr>
            <td class="forumnamecol dedicatedtolink"><a href="${fc.url('forums.forum', forum_id=forum.forum_id)}">${forum.name}</a></td>
            <td class="forumthreadcountcol">${forum.thread_count}</td>
            % if fc.req.has_named_permission(group, u'edit_forums'):
            <td class="forumoptionscol">
                <a href="${fc.url('forums.edit_forum', forum_id=forum.forum_id)}">(edit)</a>
                <a href="${fc.url('forums.move_forum', forum_id=forum.forum_id, direction=u'up')}" class="confirm">(up)</a>
                <a href="${fc.url('forums.move_forum', forum_id=forum.forum_id, direction=u'down')}" class="confirm">(down)</a>
                <a href="${fc.url('forums.delete_forum', forum_id=forum.forum_id)}" class="confirm">(delete)</a>
            </td>
            % endif
        </tr>
        % endif
        % endfor
    </tbody>
</table>
% endif