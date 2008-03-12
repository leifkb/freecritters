<%inherit file="mail_layout.mako"/>\
<%namespace file="formsuccess.mako" import="formsuccess"/>\
<%namespace file="form.mako" import="render_form"/>
<%! from simplejson import dumps %>\
<%def name="title()">Mail: ${conversation.subject}</%def>\
<%def name="head()">
<script src="${fc.url('static', fn='mailconversation.js')}" type="text/javascript"></script>
</%def>\

<script type="text/javascript">
var expanded = ${dumps(expanded)};
var collapsed = ${dumps(collapsed)};
</script>

${formsuccess(replied=u'Replied.')}

% if participation.system:
<p>This is a system-generated message.</p>
% else:
<p id="conversationheader">Conversation between you and 
<%  first = True %>\
    % for participant in conversation.participants:
    % if participant != participation:
    % if not first:
, \
    % endif
<%  first = False %>\
<a href="${fc.url('profile', username=participant.user.unformatted_username)}">${participant.user.username}</a>\
    % endif
    % endfor
.</p>
% endif

% if delete_form:
${render_form(delete_form)}
% endif

% for message in messages:
<div class="mailmessage" id="mailmessage${message.message_id}">
<p class="mailmessageheader">Sent ${datetime(message.sent)} by \
% if message.user is None:
<em>the system</em>\
% else:
<a href="${fc.url('profile', username=message.user.unformatted_username)}">${message.user.username}</a>\
% endif
% if reply_form:
 &ndash; <a href="${fc.url('mail.conversation', conversation_id=conversation.conversation_id, quote=message.message_id)}" onclick="quote('message', ${dumps(message.message)}); return false;">quote</a>\
% endif
</p>
<div class="mailmessagebody">${message.rendered_message|n}</div>
</div>
% endfor

% if reply_form:
<h3 id="reply">Reply</h3>
${render_form(reply_form)}
% endif