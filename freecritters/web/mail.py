# -*- coding: utf-8 -*-

from freecritters.model import User, MailConversation, MailParticipant, \
                               MailMessage
from freecritters.web.links import user_link, conversation_link
from freecritters.web.json import returns_json
from freecritters.web import templates
from freecritters.web.util import redirect
from freecritters.web.form import Form, HiddenField, TextField, TextArea, \
                                  SubmitButton, SelectMenu, LengthValidator
from freecritters.web.modifiers import UserModifier, FormTokenValidator, \
                                       HtmlModifier, NotMeValidator
from freecritters.web.paginator import Paginator
from freecritters.web.application import FreeCrittersResponse
from freecritters.web.exceptions import Error404, Error403
from storm.locals import Desc
from datetime import datetime
import simplejson

@returns_json
def pre_mail_message_json(req):
    try:
        username = req.args['username']
    except KeyError:
        return {
            u'requested_username': None,
            u'username': None,
            u'message': None
        }
    user = User.find_user(username)
    if user is None:
        return {
            u'requested_username': username,
            u'username': None,
            u'message': None
        }
    else:
        return {
            u'requested_username': username,
            u'username': user.username,
            u'message': user.render_pre_mail_message()
        }
    
def _conversation_data(participation, conversation):
    if participation.system:
        other_participants = None
    else:
        other_participants = []
        for participant in conversation.participants:
            if participant != participation:
                other_participants.append({
                    u'link': user_link(participant.user),
                    u'username': participant.user.username
                })
    return {
        u'id': participation.conversation_id,
        u'new': participation.last_view is None \
             or participation.last_view < participation.last_change,
        u'subject': conversation.subject,
        u'link': conversation_link(conversation),
        u'other_participants': other_participants,
        u'last_change': participation.last_change
    }

                         
def _inbox_data(req, where_clause, limit, offset=0):
    participations = req.store.find((MailParticipant, MailConversation),
        where_clause,
        MailParticipant.conversation_id==MailConversation.conversation_id
    ).order_by(Desc(MailParticipant.last_change))[offset:offset+limit]    
    return [_conversation_data(participation, conversation)
            for (participation, conversation) in participations]

def _message_data(message):
    result = {
        u'subject': message.conversation.subject,
        u'message': message.rendered_message,
        u'conversation_id': message.conversation_id,
        u'id': message.message_id,
        u'sent': message.sent
    }
    if message.user is None:
        result[u'username'] = None
    else:
        result[u'username'] = message.user.username
    return result
    
def _inbox_rss_data(req, limit, offset=0):
    where_clause = MailParticipant.where_clause(req.user)
    messages = MailMessage.find(
        where_clause,
        MailMessage.user_id!=req.user.user_id,
        MailParticipant.conversation_id==MailMessage.conversation_id
    ).order_by(Desc(MailMessage.sent))[offset:offset+limit]
    messages = [_message_data(message) for message in messages]
    result = {
        u'messages': messages
    }
    if messages:
        result[u'last_change'] = messages[0][u'sent']
    else:
        result[u'last_change'] = datetime(2000, 1, 1) # Arbitrary old date
    return result
    
def inbox(req):
    req.check_permission(u'view_mail')
    req.user.last_inbox_view = datetime.utcnow()
    where_clause = MailParticipant.where_clause(req.user)
    paginator = Paginator(req, MailParticipant.find(where_clause).count())
    context = {
        'conversations': _inbox_data(req, where_clause, **paginator.kwargs),
        'paginator': paginator,
        'form_token': req.form_token(),
        'can_send': req.has_permission(u'send_mail'),
        'can_delete': req.has_permission(u'delete_mail')
    }
    return req.render_template('inbox.html', context)

def inbox_rss(req):
    req.check_permission_rss(u'view_mail')
    return FreeCrittersResponse(
        req.render_template_to_string('inbox.rss', _inbox_rss_data(req, 30)),
        [('Content-Type', 'application/rss+xml')]
    )
    
class SendForm(Form):
    method = u'post'
    action = u'/mail/send'
    fields = [
        HiddenField(u'form_token', modifiers=[FormTokenValidator()]),
        TextField(u'user', u'To',
                  modifiers=[UserModifier(), NotMeValidator()]),
        TextField(u'subject', u'Subject',
                  max_length=MailConversation.max_subject_length,
                  size=42,
                  modifiers=[LengthValidator(2)]),
        TextArea(u'message', u'Message',
                 modifiers=[LengthValidator(2), HtmlModifier()]),
        SubmitButton(title=u'Send', id_=u'submit'),
        SubmitButton(u'preview', u'Preview')
    ]
    
def send(req):
    req.check_permission(u'send_mail')
    defaults = {
        u'form_token': req.form_token()
    }
    if 'user' in req.args:
        user = User.find_user(req.args['user'])
        if user is not None:
            pre_mail_message = user.render_pre_mail_message()
            defaults['user'] = user
        else:
            pre_mail_message = None
    else:
        user = None
        pre_mail_message = None
    form = SendForm(req, defaults)
    values = form.values_dict()
    if form.was_filled and not form.errors and u'preview' not in values:
        conversation = MailConversation(values[u'subject']).save().save()
        participant1 = MailParticipant(conversation, req.user).save()
        participant2 = MailParticipant(conversation, values[u'user']).save()
        message = MailMessage(conversation, req.user,
                              values[u'message'][0], values[u'message'][1]).save()
        req.store.flush()
        req.user.last_inbox_view = datetime.utcnow()
        req.redirect(eq, HttpFound, conversation_link(conversation).encode('utf8'))
    else:
        if u'preview' in values and form.was_filled and not form.errors:
            preview = values[u'message'][1]
        else:
            preview = None
        context = {
            'form': form.generate(),
            'preview': preview
        }
        if user is not None:
            context['username'] = user.username
            context['pre_mail_message'] = pre_mail_message
        return req.render_template('sendmail.html', context)
        
class ReplyForm(Form):
    method = u'post'
    fields = [
        HiddenField(u'form_token', modifiers=[FormTokenValidator()]),
        TextArea(u'message', u'Message',
                 modifiers=[LengthValidator(2), HtmlModifier()]),
        SubmitButton(title=u'Send', id_=u'submit'),
        SubmitButton(u'preview', u'Preview')
    ]

class DeleteForm(Form):
    method = u'post'
    fields = [
        HiddenField(u'delete_form_token', modifiers=[FormTokenValidator()]),
        SubmitButton(title=u'Delete', id_=u'deletesubmit')
    ]
    
def conversation(req, conversation_id):
    req.check_permission(u'view_mail')
    conversation = MailConversation.get(conversation_id)
    if conversation is None:
        raise Error404()
    if not conversation.can_be_viewed_by(req.user, req.subaccount):
        raise Error403()
    system = False
    other_participants = []
    for participant in conversation.participants:
        if participant.user == req.user:
            participant.last_view = datetime.utcnow()
            if participant.system:
                system = True
            participation = participant
        else:
            other_participants.append({
                u'link': user_link(participant.user),
                u'username': participant.user.username
            })
    
    if req.has_permission(u'delete_mail'):
        defaults = {
            u'delete_form_token': req.form_token()
        }
        delete_form = DeleteForm(req, defaults)
        delete_form.action = u'/mail/%s' % conversation.conversation_id
        if delete_form.was_filled and not delete_form.errors:
            participation.delete()
            req.redirect('mail.inbox')
        delete_form = delete_form.generate()
        
    else:
        delete_form = None
            
    if conversation.can_be_replied_to_by(req.user, req.subaccount) \
       and req.has_permission(u'send_mail'):
        defaults = {
            u'form_token': req.form_token(),
        }
        if 'quote' in req.args and req.args['quote'].isdigit():
            quoted_id = int(req.args['quote'])
            quoted_message = MailMessage.get(quoted_id)
            if quoted_message is not None \
               and quoted_message.conversation == conversation:
                defaults[u'message'] = (
                    u'<blockquote>%s</blockquote>\n' % quoted_message.message,
                    u'<blockquote>%s</blockquote>\n'
                        % quoted_message.rendered_message
                )
        reply_form = ReplyForm(req, defaults)
        reply_form.action = u'/mail/%s/reply' % conversation.conversation_id 
        reply_form = reply_form.generate()
    else:
        reply_form = None
        reply_successful = False
        
    last_expanded_sender = None
    messages = []
    expanded = []
    collapsed = []
    for message in conversation.messages:
        if last_expanded_sender is not None and last_expanded_sender != message.user_id:
            collapsed += expanded
            expanded = []
        last_expanded_sender = message.user_id
        expanded.append(message.message_id)
        sender = {
            u'link': user_link(message.user),
            u'username': message.user.username
        }
        messages.append({
            u'id': message.message_id,
            u'sender': sender,
            u'sent': message.sent,
            u'message': message.rendered_message,
            u'quote_link': u'/mail/%s?quote=%s#reply'
                % (conversation.conversation_id, message.message_id),
            u'quote_jsstring': simplejson.dumps(message.message)
        })
    context = {
        'subject': conversation.subject,
        'messages': messages,
        'system': system,
        'other_participants': other_participants,
        'reply_form': reply_form,
        'reply_successful': 'reply_successful' in req.args,
        'delete_form': delete_form,
        'can_reply': req.has_permission(u'send_mail'),
        'expanded': simplejson.dumps(expanded),
        'collapsed': simplejson.dumps(collapsed)
    }
    return req.render_template('mailconversation.html', context)

def reply(req, conversation_id):
    req.check_permission(u'send_mail')
    
    conversation = MailConversation.get(conversation_id)
    if conversation is None:
        raise Error404()
    
    if not conversation.can_be_replied_to_by(req.user, req.subaccount):
        raise Error403()
        
    defaults = {
        u'form_token': req.form_token(),
    }
    reply_form = ReplyForm(req, defaults)
    reply_form.action = u'/mail/%s/reply' % conversation.conversation_id
    values = reply_form.values_dict()
    
    if 'preview' not in values and reply_form.was_filled \
            and not reply_form.errors:
        message = MailMessage(conversation, req.user,
                              values['message'][0], values['message'][1]).save()
        for participant in conversation.participants:
            if participant.user != req.user:
                participant.last_change = datetime.utcnow()
            participant.deleted = False
        req.redirect('mail.conversation',
            conversation_id=conversation_id, reply_successful=1)
            
    if 'preview' in values and reply_form.was_filled \
            and not reply_form.errors:
        preview = values['message'][1]
    else:
        preview = None
        
    reply_form = reply_form.generate()
    context = {
        u'reply_form': reply_form,
        u'preview': preview
    }
    return req.render_template('mail_reply.html', context)
        
class MultiDeleteForm(Form):
    method = u'post'
    action = u'/mail/delete'
    
    fields = [
        HiddenField(u'form_token', modifiers=[FormTokenValidator()]),
        HiddenField(u'delete', must_be_present=False),
        HiddenField(u'page', must_be_present=False),
        SubmitButton(title=u'Delete', id_=u'submit')
    ]
    
def multi_delete(req):
    req.check_permission(u'delete_mail')
        
    defaults = {
        u'form_token': req.form_token(),
        u'delete': u','.join(req.form.getlist('del')),
        u'page': u'1'
    }
    form = MultiDeleteForm(req, defaults)
    if form.was_filled and not form.errors:
        values = form.values_dict()
        for id_ in values['delete'].split(u','):
            try:
                id_ = int(id_)
            except ValueError:
                continue
            conversation = MailConversation.get(id_)
            if conversation is None:
                continue
            participant = conversation.find_participant(req.user)
            if participant is not None:
                participant.delete()
        redirect(req, HttpFound, '/mail?page=%s' % values['page'])
    else:
        return req.render_template('multi_delete.html', form=form.generate())
