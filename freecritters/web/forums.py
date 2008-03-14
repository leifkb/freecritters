from freecritters.web.globals import fc
from freecritters.web.paginator import Paginator
from freecritters.model import Session, Forum, Thread, Post, GroupRole, \
                               GroupMember, Group
from freecritters.web.form import Form, TextField, TextArea, SubmitButton, \
                                  LengthValidator, NotBlankValidator
from freecritters.web.modifiers import FormTokenField, HtmlModifier
from freecritters.web.exceptions import Error404
from freecritters.web.util import confirm
from freecritters.web.groups import edit_group_forum
from sqlalchemy import desc, outerjoin
from sqlalchemy.orm import eagerload

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
    req.check_permission_and_group_permission(forum.group, forum.view_permission, forum.view_group_permission)
    
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
    req.check_permission_and_group_permission(
        thread.forum.group,
        thread.forum.view_permission,
        thread.forum.view_group_permission)
    
    if req.has_permission_and_group_permission(thread.forum.group,
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

def delete_thread(req, thread_id):
    thread = _get_thread(thread_id)
    req.check_named_permission(thread.forum.group, u'moderate')

    confirm(u'delete this thread')
    
    Session.delete(thread)
    req.redirect('forums.forum', forum_id=thread.forum.forum_id, thread_deleted=1)

def create_post(req, thread_id):
    thread = _get_thread(thread_id)
    req.check_permission_and_group_permission(
        thread.forum.group,
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
              modifiers=[NotBlankValidator()]),
    TextArea(u'message', u'Message',
             modifiers=[NotBlankValidator(), HtmlModifier()]),
    SubmitButton(id_=u'submitbtn', title=u'Create thread'),
    SubmitButton(u'preview', u'Preview'))


def delete_post(req, post_id):
    post = Post.query.options(
        eagerload('thread'),
        eagerload('thread.forum'),
        eagerload('thread.forum.group')
    ).get(post_id)
    if post is None:
        return None
    req.check_named_permission(post.thread.forum.group, u'moderate')
    
    confirm(u'delete this post')
    
    Session.delete(post)
    req.redirect('forums.thread', thread_id=post.thread.thread_id, post_deleted=1)

def create_thread(req, forum_id):
    forum = Forum.query.options(
        eagerload('group')
    ).get(forum_id)
    if forum is None:
        return None
    req.check_permission_and_group_permission(
        forum.group,
        forum.create_thread_permission,
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

def edit_forum(req, forum_id):
    forum = Forum.query.options(
        eagerload('view_permission'),
        eagerload('create_post_permission'),
        eagerload('create_thread_permission'),
        eagerload('view_group_permission'),
        eagerload('create_post_group_permission'),
        eagerload('create_thread_group_permission')
    ).get(forum_id)
    if forum is None:
        return None
    
    if forum.group is None:
        pass
    else:
        return edit_group_forum(req, forum)

def delete_forum(req, forum_id):
    forum = Forum.query.get(forum_id)
    if forum is None:
        return None
    req.check_named_permission(forum.group, u'edit_forums')
    confirm(u'delete that forum')
    Session.delete(forum)
    req.redirect('forums', group_id=forum.group and forum.group.group_id, deleted=1)

def move_forum(req, forum_id, direction=u'up'):
    forum = Forum.query.get(forum_id)
    if forum is None:
        return None
    req.check_named_permission(forum.group, u'edit_forums')
    confirm(u'move that forum')
    if direction == u'up':
        forum.move_up()
    else:
        forum.move_down()
    req.redirect('forums', group_id=forum.group and forum.group.group_id)