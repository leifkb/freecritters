from freecritters.web.globals import fc
from freecritters.web.paginator import Paginator
from freecritters.model import Session, Forum, Thread, Post, GroupRole, \
                               GroupMember, Group
from freecritters.web.form import Form, TextField, TextArea, SubmitButton, \
                                  LengthValidator
from freecritters.web.modifiers import FormTokenField, HtmlModifier
from freecritters.web.exceptions import Error404
from sqlalchemy import desc, outerjoin
from sqlalchemy.orm import eagerload

def _check_forum_permissions(group, permission, group_permission):
    fc.req.check_permission(permission)
    if group is not None:
        fc.req.check_group_permission(group, group_permission)

def _has_forum_permissions(group, permission, group_permission):
    result = fc.req.has_permission(permission)
    if group is not None:
        result = result and fc.req.has_group_permission(group, group_permission)
    return result

def forums(req, group_id=None):
    if group_id is None:
        group = None
        forums = Forum.query.filter_by(group_id=None)
    else:
        group = Group.query.get(group_id)
        if group is None:
            req.check_group_permission(group, None)
        forums = group.forums
    
    forums = forums.options(
        eagerload('view_permission'),
        eagerload('view_group_permission')
    ).order_by(Forum.order_num).all()
    
    fc.group = group # Pool closed due to AIDS and kludgery
    return req.render_template('forums.mako',
        group=group,
        forums=forums)
    
    
thread_paginator = Paginator()

def forum(req, forum_id):
    forum = Forum.query.get(forum_id)
    if forum is None:
        return None
    _check_forum_permissions(forum.group, forum.view_permission, forum.view_group_permission)
    
    threads = forum.threads.order_by(desc(Thread.last_post))
    threads = threads.options(eagerload('user'))
    paginated = thread_paginator(req, threads, forum.thread_count)
    fc.group = forum.group # Kludge to allow dynamic layout selection
    return req.render_template('forum.mako',
        group=forum.group,
        forum=forum,
        paginator=paginated,
        threads=paginated.all())

def _get_thread(thread_id):
    thread = Thread.query.options(
        eagerload('forum'),
        eagerload('forum.group'),
    ).get(thread_id)
    if thread is None:
        raise Error404()
    return thread

post_paginator = Paginator(50)
create_post_form = Form(u'post', None,
    FormTokenField(),
    TextArea(u'message', u'Message',
              modifiers=[LengthValidator(2), HtmlModifier()]),
    SubmitButton(id_=u'submitbtn', title=u'Post'),
    SubmitButton(u'preview', u'Preview'))

def thread(req, thread_id):
    thread = _get_thread(thread_id)
    _check_forum_permissions(thread.forum.group, thread.forum.view_permission,
                             thread.forum.view_group_permission)
    
    if _has_forum_permissions(thread.forum.group,
                              thread.forum.create_post_permission,
                              thread.forum.create_post_group_permission):
        defaults = {}
        try:
            quote_id = int(req.args['quote'])
            quote_post = Post.query.get(quote_id)
            if quote_post is not None and quote_post.thread == thread:
                defaults[u'message'] = (
                    u'<blockquote>%s</blockquote>\n' % quote_post.message,
                    u'<blockquote>%s</blockquote>' % quote_post.rendered_message
                )
        except (ValueError, KeyError):
            pass
        results = create_post_form(req, defaults)
        results.action = 'forums.create_post', dict(thread_id=thread_id)
    else:
        results = None
    
    posts = thread.posts.options(
        eagerload('membership'),
        eagerload('membership.group_role'),
        eagerload('user'),
        eagerload('user.role')
    ).order_by(Post.created)
    paginated = post_paginator(req, posts, thread.post_count)
    fc.group = thread.forum.group # Hooray for kludges!
    return req.render_template('thread.mako',
        group=thread.forum.group,
        forum=thread.forum,
        thread=thread,
        paginator=paginated,
        posts=paginated.all(),
        form=results)

def create_post(req, thread_id):
    thread = _get_thread(thread_id)
    _check_forum_permissions(thread.forum.group,
                             thread.forum.create_post_permission,
                             thread.forum.create_post_group_permission)
    
    results = create_post_form(req)
    results.action = 'forums.create_post', dict(thread_id=thread_id)
    
    if results.successful and u'preview' not in results:
        post = Post(thread, req.user, *results[u'message'])
        Session.save(post)
        Session.flush()
        req.redirect('forums.thread', None, 'post%s' % post.post_id,
                     thread_id=thread.thread_id, page='0')
    else:
        if results.successful:
            preview = results[u'message'][1]
        else:
            preview = None
        fc.group = thread.forum.group
        return req.render_template('create_post.mako',
                                   preview=preview,
                                   group=thread.forum.group,
                                   forum=thread.forum,
                                   thread=thread,
                                   form=results)

create_thread_form = Form(u'post', None,
    FormTokenField(),
    TextField(u'subject', u'Subject',
              size=42,
              max_length=Thread.max_subject_length,
              modifiers=[LengthValidator(2)]),
    TextArea(u'message', u'Message',
             modifiers=[LengthValidator(2), HtmlModifier()]),
    SubmitButton(id_=u'submitbtn', title=u'Create thread'),
    SubmitButton(id_=u'preview', title=u'Preview'))

def create_thread(req, forum_id):
    forum = Forum.query.options(
        eagerload('group')
    ).get(forum_id)
    if forum is None:
        return None
    _check_forum_permissions(forum.group, forum.create_thread_permission,
                             forum.create_thread_group_permission)
    
    results = create_thread_form(req)
    results.action = 'forums.create_thread', dict(forum_id=forum_id)
    
    if results.successful and u'preview' not in results:
        thread = Thread(forum, req.user, results[u'subject'])
        post = Post(thread, req.user, *results[u'message'])
        Session.save(thread)
        Session.flush()
        req.redirect('forums.thread', thread_id=thread.thread_id)
    else:
        if results.successful:
            preview = results[u'message'][1]
        else:
            preview = None
        fc.group = forum.group
        return req.render_template('create_thread.mako',
            preview=preview,
            group=forum.group,
            forum=forum,
            form=results)