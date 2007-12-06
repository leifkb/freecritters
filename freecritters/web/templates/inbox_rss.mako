<?xml version="1.0"?>
<rss version="2.0">
    <channel>
        <title>${fc.req.config.site.name} mail</title>
        <link>${fc.url('mail.inbox')}</link>
        <description>${fc.req.user.username}'s mail on ${fc.req.config.site.name}.</description>
        <pubDate>${rss_time(last_change)}</pubDate>
        <lastBuildDate>${rss_time(last_change)}</lastBuildDate>
        <docs>http://blogs.law.harvard.edu/tech/rss</docs>
        <generator>freeCritters</generator>
        % for message in messages:
<% message_url = '%s#messageurl%s' % (fc.url('mail.conversation', None, True, conversation_id=message.conversation_id), message.message_id) %>\
        <item>
            <title>${message.conversation.subject}\
% if message.user is not None:
 from ${message.user.username}\
% endif
</title>
            <description>${message.rendered_message}</description>
            <link>${message_url}</link>
            <pubDate>${rss_time(message.sent)}</pubDate>
            <guid>${message_url}</guid>
        </item>
        % endfor
    </channel>
</rss>