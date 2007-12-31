<%inherit file="maybe_group_layout.mako"/>\
<%def name="tabs()"><%
    return [
        Tab('Forum', 'forums.forum', forum_id=forum.forum_id),
        Tab('Create Thread', 'forums.create_thread', forum_id=forum.forum_id)
    ]
%></%def>\
${next.body()}