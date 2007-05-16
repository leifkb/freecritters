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
from colubrid.utils import MultiDict
from colubrid.exceptions import AccessDenied, HttpFound, PageNotFound
from sqlalchemy import desc, lazyload
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
    user = User.find_user(req.sess, username)
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
        
def inbox(req):
    req.check_permission(None)
    req.login.user.last_inbox_view = datetime.utcnow()
    query = req.sess.query(MailParticipant)
    where_clause = MailParticipant.where_clause(req.login.user)
    paginator = Paginator(req, query.count(where_clause))
    participations = query.select(where_clause,
                                  order_by=desc(MailParticipant.c.last_change),
                                  **paginator.kwargs)
    conversation_participants = {}
    conversation_ids = [participation.conversation_id \
                         for participation in participations]
    participants = query.options(lazyload('conversation')).select(
        MailParticipant.c.conversation_id.in_(*conversation_ids),
        order_by=MailParticipant.c.conversation_id
    )
    for participant in participants:
        conversation_participants.setdefault(participant.conversation_id, []) \
            .append(participant)
            
    conversations = []
    for participation in participations:
        if participation.system:
            other_participants = None
        else:
            other_participants = []
            for participant \
             in conversation_participants[participation.conversation_id]:
                if participant != participation:
                    other_participants.append({
                        u'link': user_link(participant.user),
                        u'username': participant.user.username
                    })
        conversations.append({
            u'id': participation.conversation_id,
            u'new': participation.last_view is None \
                 or participation.last_view < participation.last_change,
            u'subject': participation.conversation.subject,
            u'link': conversation_link(participation.conversation),
            u'other_participants': other_participants
        })
    context = {
        u'conversations': conversations,
        u'paginator': paginator,
        u'form_token': req.login.form_token(),
        u'can_send': req.has_permission('send_mail'),
        u'can_delete': req.has_permission('delete_mail')
    }
    return templates.factory.render('inbox', req, context)

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
        u'form_token': req.login.form_token()
    }
    if 'user' in req.args:
        user = User.find_user(req.sess, req.args['user'])
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
        conversation = MailConversation(values[u'subject'])
        req.sess.save(conversation)
        participant1 = MailParticipant(conversation, req.login.user)
        req.sess.save(participant1)
        participant2 = MailParticipant(conversation, values[u'user'])
        req.sess.save(participant2)
        message = MailMessage(conversation, req.login.user,
                              values[u'message'][0], values[u'message'][1])
        req.sess.save(message)
        req.login.user.last_inbox_view = datetime.utcnow()
        req.sess.flush()
        redirect(req, HttpFound, conversation_link(conversation).encode('utf8'))
    else:
        if u'preview' in values and form.was_filled and not form.errors:
            preview = values[u'message'][1]
        else:
            preview = None
        context = {
            u'form': form.generate(),
            u'preview': preview
        }
        if user is not None:
            context[u'username'] = user.username
            context[u'pre_mail_message'] = pre_mail_message
        return templates.factory.render('sendmail', req, context)
        
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
    conversation = req.sess.query(MailConversation).get(conversation_id)
    if conversation is None:
        raise PageNotFound()
    if not conversation.can_be_viewed_by(req.login.user, req.login.subaccount):
        raise AccessDenied()
    system = False
    other_participants = []
    for participant in conversation.participants:
        if participant.user == req.login.user:
            participant.last_view = datetime.utcnow()
            if participant.system:
                system = True
            participation = participant
        else:
            other_participants.append({
                u'link': user_link(participant.user),
                u'username': participant.user.username
            })
    
    if req.has_permission('delete_mail'):
        defaults = {
            u'delete_form_token': req.login.form_token()
        }
        delete_form = DeleteForm(req, defaults)
        delete_form.action = u'/mail/%s' % conversation.conversation_id
        if delete_form.was_filled and not delete_form.errors:
            participation.delete()
            redirect(req, HttpFound, '/mail')
        delete_form = delete_form.generate()
        
    else:
        delete_form = None
            
    if conversation.can_be_replied_to_by(req.login.user,
                                         req.login.subaccount) \
       and req.has_permission(u'send_mail'):
        defaults = {
            u'form_token': req.login.form_token(),
        }
        if 'quote' in req.args and req.args['quote'].isdigit():
            quoted_id = int(req.args['quote'])
            quoted_message = req.sess.query(MailMessage).get(quoted_id)
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
        
    messages = []
    for message in conversation.messages:
        sender = {
            u'link': user_link(message.user),
            u'username': message.user.username
        }
        messages.append({
            u'sender': sender,
            u'sent': message.sent,
            u'message': message.rendered_message,
            u'quote_link': u'/mail/%s?quote=%s#reply'
                % (conversation.conversation_id, message.message_id),
            u'quote_jsstring': simplejson.dumps(message.message)
        })
    context = {
        u'subject': conversation.subject,
        u'messages': messages,
        u'system': system,
        u'other_participants': other_participants,
        u'reply_form': reply_form,
        u'reply_successful': 'reply_successful' in req.args,
        u'delete_form': delete_form,
        u'can_reply': req.has_permission(u'send_mail')
    }
    return templates.factory.render('mailconversation', req, context)

def reply(req, conversation_id):
    # Hooray for nearly-duplicated code!
    req.check_permission(u'send_mail')
    conversation = req.sess.query(MailConversation).get(conversation_id)
    if conversation is None:
        raise PageNotFound()
    if not conversation.can_be_replied_to_by(req.login.user, req.login.subaccount):
        raise AccessDenied()
    defaults = {
        u'form_token': req.login.form_token(),
    }
    reply_form = ReplyForm(req, defaults)
    reply_form.action = u'/mail/%s/reply' % conversation.conversation_id
    values = reply_form.values_dict()
    if 'preview' not in values and reply_form.was_filled \
            and not reply_form.errors:
        message = MailMessage(conversation, req.login.user,
                              values['message'][0], values['message'][1])
        for participant in conversation.participants:
            if participant.user != req.login.user:
                participant.last_change = datetime.utcnow()
            participant.deleted = False
        req.sess.save(message)
        redirect(HttpFound,
            '/mail/%s?reply_successful=1' % conversation.conversation_id)
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
    return templates.factory.render('mail_reply', req, context)
        
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
        u'form_token': req.login.form_token(),
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
            conversation = req.sess.query(MailConversation).get(id_)
            if conversation is None:
                continue
            participant = conversation.find_participant(req.login.user)
            if participant is not None:
                participant.delete()
        redirect(req, HttpFound, '/mail?page=%s' % values['page'])
    else:
        context = {
            u'form': form.generate()
        }
        return templates.factory.render('multi_delete', req, context)
