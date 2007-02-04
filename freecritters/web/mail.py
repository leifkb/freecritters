# -*- coding: utf-8 -*-

from freecritters.model import User, MailConversation, MailParticipant, \
                               MailMessage
from freecritters.web.links import user_link, conversation_link
from freecritters.web.json import returns_json
from freecritters.web import templates
from freecritters.web.form import Form, HiddenField, TextField, TextArea, \
                                  SubmitButton, SelectMenu, LengthValidator
from freecritters.web.modifiers import UserModifier, FormTokenValidator, \
                                       TextFormatModifier, NotMeValidator
from freecritters.textformats import text_formats
from freecritters.web.paginator import Paginator
from colubrid.utils import MultiDict
from colubrid.exceptions import AccessDenied, HttpFound, PageNotFound
from sqlalchemy import desc
from datetime import datetime

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
    if req.login is None:
        raise AccessDenied()
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
    participants = query.select(
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
            u'new': participation.last_view is None \
                 or participation.last_view < participation.last_change,
            u'subject': participation.conversation.subject,
            u'link': conversation_link(participation.conversation),
            u'other_participants': other_participants
        })
    context = {u'conversations': conversations, u'paginator': paginator}
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
                 modifiers=[LengthValidator(2),
                            TextFormatModifier(u'format')]),
        SelectMenu(u'format', u'Format', options=text_formats),
        SubmitButton(title=u'Send', id_=u'submit')
    ]
    
def send(req):
    if req.login is None:
        raise AccessDenied()
    defaults = {
        u'format': req.login.user.default_format,
        u'form_token': req.login.form_token()
    }
    if u'user' in req.args:
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
    if form.was_filled and not form.errors:
        values = form.values_dict()
        conversation = MailConversation(values['subject'])
        req.sess.save(conversation)
        participant1 = MailParticipant(conversation, req.login.user)
        req.sess.save(participant1)
        participant2 = MailParticipant(conversation, values['user'])
        req.sess.save(participant2)
        message = MailMessage(conversation, req.login.user,
                              values['message'][0], values['format'],
                              values['message'][1])
        req.sess.save(message)
        req.login.user.last_inbox_view = datetime.utcnow()
        req.sess.flush()
        raise HttpFound(conversation_link(conversation))
    else:
        context = {
            u'form': form.generate(),
        }
        if user is not None:
            context['username'] = user.username
            context['pre_mail_message'] = pre_mail_message
        return templates.factory.render('sendmail', req, context)
        
class ReplyForm(Form):
    method = u'post'
    fields = [
        HiddenField(u'form_token', modifiers=[FormTokenValidator()]),
        TextArea(u'message', u'Message',
                 modifiers=[LengthValidator(2),
                            TextFormatModifier(u'format')]),
        SelectMenu(u'format', u'Format', options=text_formats),
        SubmitButton(title=u'Send', id_=u'submit')
    ]
        
def conversation(req, conversation_id):
    if req.login is None:
        raise AccessDenied()
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
            self_found = True
        else:
            other_participants.append({
                u'link': user_link(participant.user),
                u'username': participant.user.username
            })
    if conversation.can_be_replied_to_by(req.login.user, req.login.subaccount):
        defaults = {
            u'form_token': req.login.form_token(),
            u'format': req.login.user.default_format
        }
        reply_form = ReplyForm(req, defaults)
        reply_form.action = u'/mail/%s#reply' % conversation.conversation_id
        if reply_form.was_filled and not reply_form.errors:
            values = reply_form.values_dict()
            message = MailMessage(conversation, req.login.user,
                                  values['message'][0], values['format'],
                                  values['message'][1])
            for participant in conversation.participants:
                if participant.user != req.login.user:
                    participant.last_change = datetime.utcnow()
                participant.deleted = False
            req.sess.save(message)
            reply_successful = True
            reply_form = ReplyForm(req, defaults, MultiDict())
        else:
            reply_successful = False
        form = reply_form.generate()
    else:
        form = None
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
            u'message': message.rendered_message
        })
    context = {
        u'subject': conversation.subject,
        u'messages': messages,
        u'system': system,
        u'other_participants': other_participants,
        u'reply_form': form,
        u'reply_successful': reply_successful
    }
    return templates.factory.render('mailconversation', req, context)
