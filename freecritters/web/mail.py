# -*- coding: utf-8 -*-

from freecritters.model import User, MailConversation, MailParticipant, \
                               MailMessage, Session
from freecritters.web.util import returns_json
from freecritters.web.form import Form, HiddenField, TextField, TextArea, \
                                  SubmitButton, SelectMenu, LengthValidator
from freecritters.web.modifiers import UserModifier, FormTokenField, \
                                       HtmlModifier, NotMeValidator
from freecritters.web.paginator import Paginator
from freecritters.web.application import Response
from freecritters.web.exceptions import Error404, Error403
from datetime import datetime
from sqlalchemy import desc, and_
from sqlalchemy.orm import eagerload
import simplejson

@returns_json
def pre_mail_message_json(req, username):
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
            u'message': user.rendered_pre_mail_message
        }

inbox_paginator = Paginator()

def inbox(req):
    req.check_permission(u'view_mail')

    participations = MailParticipant.find(req.user).options(
        eagerload('conversation'),
        eagerload('conversation.participants'),
        eagerload('conversation.participants.user')
    ).order_by(
        desc(MailParticipant.last_change)
    )
    
    req.user.last_inbox_view = datetime.utcnow()
    
    paginated = inbox_paginator(req, participations)
        
    return req.render_template('inbox.mako',
        participations=paginated.all(),
        paginator=paginated,
        form_token=req.form_token(),
        can_send=req.has_permission(u'send_mail'),
        can_delete=req.has_permission(u'delete_mail')
    )

def inbox_rss(req):
    req.check_permission_rss(u'view_mail')
    messages = MailMessage.query.join(['conversation', 'participants']).filter(and_(
        MailParticipant.user_id==req.user.user_id,
        MailParticipant.deleted==False,
        MailMessage.user_id!=req.user.user_id
    )).order_by(desc(MailMessage.sent))[:30].all()
    if messages:
        last_change = messages[0].sent
    else:
        last_change = datetime(2000, 1, 1) # Arbitrary old date
    req.check_modified(last_change)
    return Response(
        req.render_template_to_string('inbox_rss.mako', messages=messages, last_change=last_change),
        mimetype='application/rss+xml; charset=utf-8'
    ).last_modified(last_change)
    
send_form = Form(u'post', 'mail.send',
    FormTokenField(),
    TextField(u'user', u'To',
              modifiers=[UserModifier(), NotMeValidator()]),
    TextField(u'subject', u'Subject',
              max_length=MailConversation.max_subject_length,
              size=42,
              modifiers=[LengthValidator(2)]),
    TextArea(u'message', u'Message',
             modifiers=[LengthValidator(2), HtmlModifier()]),
    SubmitButton(title=u'Send', id_=u'submit'),
    SubmitButton(u'preview', u'Preview'))
    
def send(req):
    req.check_permission(u'send_mail')
    defaults = {}
    if 'user' in req.args:
        user = User.find_user(req.args['user'])
        if user is not None:
            defaults[u'user'] = user
    form = send_form(req, defaults)
    if form.successful and u'preview' not in form:
        conversation = MailConversation(form[u'subject'])
        participant1 = MailParticipant(conversation, req.user)
        participant2 = MailParticipant(conversation, form[u'user'])
        message = MailMessage(conversation, req.user,
                              form[u'message'][0], form[u'message'][1])
        Session.save(conversation)
        Session.save(participant1)
        Session.save(participant2)
        Session.save(message)
        req.user.last_inbox_view = datetime.utcnow()
        Session.flush()
        req.redirect('mail.conversation', conversation_id=conversation.conversation_id)
    else:
        if u'preview' in form and u'message' in form:
            preview = form[u'message'][1]
        else:
            preview = None
        return req.render_template('send_mail.mako',
            form=form,
            preview=preview,
            user=form.get(u'user'))
        
reply_form = Form(u'post', None,
    FormTokenField(),
    TextArea(u'message', u'Message',
             modifiers=[LengthValidator(2), HtmlModifier()]),
    SubmitButton(title=u'Send', id_=u'submit'),
    SubmitButton(u'preview', u'Preview'))

delete_form = Form(u'post', None,
    FormTokenField(),
    SubmitButton(title=u'Delete', id_=u'submit'),
    id_prefix=u'delete_')
    
def conversation(req, conversation_id):
    req.check_permission(u'view_mail')
    conversation = MailConversation.query.get(conversation_id)
    if conversation is None:
        return None
    participation = conversation.find_participant(req.user)
    if participation is None:
        raise Error403()
    participation.last_view = datetime.utcnow()
    
    if req.has_permission(u'delete_mail'):
        delete_form_results = delete_form(req)
        delete_form_results.action = 'mail.conversation', dict(conversation_id=conversation.conversation_id)
        if delete_form_results.successful:
            participation.delete()
            req.redirect('mail.inbox')
    else:
        delete_form_results = None
            
    if req.has_permission(u'send_mail') and not participation.system:
        defaults = {}
        if 'quote' in req.args and req.args['quote'].isdigit():
            quoted_id = int(req.args['quote'])
            quoted_message = MailMessage.query.get(quoted_id)
            if quoted_message is not None \
               and quoted_message.conversation == conversation:
                defaults[u'message'] = (
                    u'<blockquote>%s</blockquote>\n' % quoted_message.message,
                    u'<blockquote>%s</blockquote>\n' % quoted_message.rendered_message
                )
        reply_form_results = reply_form(req, defaults)
        reply_form_results.action = 'mail.reply', dict(conversation_id=conversation.conversation_id) 
    else:
        reply_form_results = None
        reply_successful = False
        
    last_expanded_sender = None
    expanded = []
    collapsed = []
    messages = conversation.messages.order_by(MailMessage.sent).all()
    for message in messages:
        if last_expanded_sender is not None and last_expanded_sender != message.user_id:
            collapsed += expanded
            expanded = []
        last_expanded_sender = message.user_id
        expanded.append(message.message_id)
    return req.render_template('mail_conversation.mako',
        participation=participation,
        conversation=conversation,
        messages=messages,
        reply_form=reply_form_results,
        reply_successful='reply_successful' in req.args,
        delete_form=delete_form_results,
        can_reply=req.has_permission(u'send_mail'),
        expanded=expanded,
        collapsed=collapsed)

def reply(req, conversation_id):
    req.check_permission(u'send_mail')
    
    conversation = MailConversation.query.get(conversation_id)
    if conversation is None:
        return None
    
    participation = conversation.find_participant(req.user)
    if participation is None:
        raise Error403()
    
    reply_form_results = reply_form(req)
    reply_form_results.action = 'mail.reply', dict(conversation_id=conversation.conversation_id)
    
    if reply_form_results.successful and u'preview' not in reply_form_results:
        message = MailMessage(conversation, req.user,
                              reply_form_results['message'][0], reply_form_results['message'][1])
        Session.save(message)
        for participant in conversation.participants:
            if participant != participation:
                participant.last_change = datetime.utcnow()
            participant.deleted = False
        req.redirect('mail.conversation',
            conversation_id=conversation_id, reply_successful=1)
            
    if reply_form_results.successful and u'preview' in reply_form_results:
        preview = reply_form_results['message'][1]
    else:
        preview = None
    
    return req.render_template('mail_reply.mako',
        reply_form=reply_form_results,
        preview=preview)

multi_delete_form = Form(u'post', 'mail.multi_delete',
    FormTokenField(),
    HiddenField(u'delete', must_be_present=False),
    HiddenField(u'page', must_be_present=False),
    SubmitButton(title=u'Delete', id_=u'submit'))

def multi_delete(req):
    req.check_permission(u'delete_mail')
        
    defaults = {
        u'delete': u','.join(req.form.getlist('del')),
        u'page': u'1'
    }
    results = multi_delete_form(req, defaults)
    if results.successful:
        for id_ in results[u'delete'].split(u','):
            try:
                id_ = int(id_)
            except ValueError:
                continue
            conversation = MailConversation.query.get(id_)
            if conversation is None:
                continue
            participation = conversation.find_participant(req.user)
            if participation is not None:
                participation.delete()
        req.redirect('mail.inbox', page=results[u'page'])
    else:
        return req.render_template('multi_delete.mako', form=results)