<%inherit file="mail_layout.mako" />
<%namespace file="paginator.mako" import="render_paginator_in_box" />
<%def name="title()">Inbox</%def>

<%def name="head()">
<link rel="alternate" type="application/rss+xml" title="RSS 2.0" href="${fc.url('mail.inbox_rss')}">
</%def>

<p>Here's your inbox, which contains all of your mail conversations.</p>
% if not participations:
<p><strong>You don't have any mail.</strong></p>
%else:
% if can_delete:
<form action="${fc.url('mail.multi_delete')}" method="post">
<div>
<input type="hidden" name="form_token" value="${form_token}">
<input type="hidden" name="page" value="${paginator.page}">
</div>
% endif
<table class="normal mailtable">
<thead>
<tr>
% if can_delete:
<th class="maildelcolumn">Del</th>
% endif
<th class="mailsubjectcolumn">Subject</th>
<th class="mailwithcolumn">With</th>
</tr>
</thead>
<tbody>
% for participation in participations:
<% conversation = participation.conversation %>
<tr\
% if participation.is_new:
 class="newmail"\
% endif 
>
% if can_delete:
<td class="maildelcolumn"><input type="checkbox" name="del" value="${conversation.conversation_id}"></td>
% endif
<td class="mailsubjectcolumn dedicatedtolink">\
% if participation.is_new:
<strong>\
%endif
<a href="${fc.url('mail.conversation', conversation_id=conversation.conversation_id)}">${conversation.subject}</a>\
% if participation.is_new:
</strong>\
% endif
</td>
<td class="mailwithcolumn dedicatedtolink">
% if participation.system:
<em>system-generated</em>
% else:
<% first = True %>
% for participant in conversation.participants:
% if participant != participation:
% if not first:
, \
% endif
<% first = false %>
<a href="${fc.url('profile', username=participant.user.unformatted_username)}">${participant.user.username}</a>
% endif
% endfor
% endif
</td>
</tr>
% endfor
</tbody>
</table>
% if can_delete:
<p id="maildeletecheckedbtncontainer"><input type="submit" value="Delete checked"></p>
</form>
% endif
${render_paginator_in_box(paginator)}
% endif