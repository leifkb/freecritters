from werkzeug.routing import Map, Rule
from werkzeug.contrib.jsrouting import generate_map
from freecritters.web.urlconverters import ColorConverter
from freecritters.web.util import http_date
from datetime import datetime
from os import stat

urls = Map([
    Rule('/', endpoint='home'),
    Rule('/register', endpoint='register'),
    Rule('/login', endpoint='login'),
    Rule('/logout', endpoint='logout'),
    Rule('/users/<username>', endpoint='profile'),
    Rule('/editprofile', endpoint='settings.edit_profile'),
    Rule('/changepassword', endpoint='settings.change_password'),
    Rule('/subaccounts/', endpoint='settings.subaccount_list'),
    Rule('/subaccounts/create', endpoint='settings.create_subaccount'),
    Rule('/subaccounts/<int:subaccount_id>/edit', endpoint='settings.edit_subaccount'),
    Rule('/subaccounts/<int:subaccount_id>/delete', endpoint='settings.delete_subaccount'),
    Rule('/subaccounts/<int:subaccount_id>/change_password', endpoint='settings.change_subaccount_password'),
    Rule('/pictures/<int:picture_id>/', defaults={'size': u'full'}, endpoint='pictures.picture'),
    Rule('/pictures/<int:picture_id>/<size>', endpoint='pictures.picture'),
    Rule('/mail/', endpoint='mail.inbox'),
    Rule('/mail/.rss', endpoint='mail.inbox_rss'),
    Rule('/mail/send', endpoint='mail.send'),
    Rule('/mail/<int:conversation_id>', endpoint='mail.conversation'),
    Rule('/mail/<int:conversation_id>/reply', endpoint='mail.reply'),
    Rule('/mail/delete', endpoint='mail.multi_delete'),
    Rule('/json/pre_mail_message/<username>', endpoint='mail.pre_mail_message_json'),
    Rule('/pets/images/<int:species_id>/<int:appearance_id>/<color:color>', endpoint='pets.pet_image'),
    Rule('/pets/create/<int:species_id>', endpoint='pets.create_pet'),
    Rule('/pets/', endpoint='pets.pet_list'),
    Rule('/pets/create/', endpoint='pets.species_list'),
    Rule('/groups/', endpoint='groups'),
    Rule('/groups/list', endpoint='groups.group_list'),
    Rule('/groups/create', endpoint='groups.create_group'),
    Rule('/groups/<int:group_id>/', endpoint='groups.group'),
    Rule('/groups/<int:group_id>/leave', endpoint='groups.leave_group'),
    Rule('/groups/<int:group_id>/members', endpoint='groups.group_members'),
    Rule('/groups/<int:group_id>/members/<username>/edit', endpoint='groups.edit_member'),
    Rule('/groups/<int:group_id>/members/<username>/remove', endpoint='groups.remove_member'),
    Rule('/groups/<int:group_id>/members/<username>/make_owner', endpoint='groups.change_owner'),
    Rule('/groups/<int:group_id>/edit', endpoint='groups.edit_group'),
    Rule('/groups/<int:group_id>/delete', endpoint='groups.delete_group'),
    Rule('/groups/<int:group_id>/edit_roles', endpoint='groups.edit_roles'),
    Rule('/groups/<int:group_id>/create_role', endpoint='groups.create_role'),
    Rule('/groups/roles/<int:role_id>/edit', endpoint='groups.edit_role'),
    Rule('/groups/roles/<int:role_id>/delete', endpoint='groups.delete_role'),
    Rule('/groups/roles/<int:role_id>/make_default', endpoint='groups.make_role_default'),
    Rule('/groups/<int:group_id>/edit_special_permissions', endpoint='groups.edit_special_permissions'),
    Rule('/groups/<int:group_id>/create_special_permission', endpoint='groups.create_special_permission'),
    Rule('/groups/special_permissions/<int:permission_id>/edit', endpoint='groups.edit_special_permission'),
    Rule('/groups/special_permissions/<int:permission_id>/delete', endpoint='groups.delete_special_permission'),
    Rule('/groups/<int:group_id>/forums', endpoint='forums'),
    Rule('/groups/<int:group_id>/create_forum', endpoint='groups.create_forum'),
    Rule('/forums/', endpoint='forums', defaults={'group_id': None}),
    Rule('/forums/<int:forum_id>/', endpoint='forums.forum'),
    Rule('/forums/<int:forum_id>/create_thread', endpoint='forums.create_thread'),
    Rule('/forums/threads/<int:thread_id>/', endpoint='forums.thread'),
    Rule('/forums/threads/<int:thread_id>/delete', endpoint='forums.delete_thread'),
    Rule('/forums/threads/<int:thread_id>/post', endpoint='forums.create_post'),
    Rule('/forums/posts/<int:post_id>/delete', endpoint='forums.delete_post'),
    Rule('/static/<path:fn>', endpoint='static'),
    Rule('/urls.js', endpoint='urls.urls_js')
], charset='utf-8', converters={'color': ColorConverter})

last_modified = datetime.utcfromtimestamp(stat(__file__).st_mtime)

def urls_js(req):
    from freecritters.web.application import Response
    req.check_modified(last_modified)
    js = 'var url_map = %s;' % generate_map(urls, None)
    response = Response(js, mimetype='application/javascript')
    return response.last_modified(last_modified, False)