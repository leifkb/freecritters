<%inherit file="layout.mako"/>\
<%def name="tabs()"><%
    return [
        Tab(u'Inbox', 'mail.inbox'),
        Tab(u'Send', 'mail.send')
    ]
%></%def>\
${next.body()}