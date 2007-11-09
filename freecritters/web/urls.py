from werkzeug.routing import Map, Rule
from freecritters.web.urlconverters import ColorConverter
from freecritters.application import Response
from freecritters.util import http_date
from datetime import datetime
from os import stat

urls = Map([
    Rule('/', endpoint='home'),
    Rule('/register', endpoint='register'),
    Rule('/login', endpoint='login'),
    Rule('/logout', endpoint='logout'),
    Rule('/users/<username>', endpoint='profile'),
    Rule('/editprofile', endpoint='settings.edit_profile'),
    Rule('/subaccounts/', endpoint='settings.subaccount_list'),
    Rule('/subaccounts/create', endpoint='settings.create_subaccount'),
    Rule('/subaccounts/<int:subaccount_id>/edit', endpoint='settings.edit_subaccount'),
    Rule('/subaccounts/<int:subaccount_id>/delete', endpoint='settings.delete_subaccount'),
    Rule('/subaccounts/<int:subaccount_id>/change_password', endpoint='settings.change_subaccount_password'),
    Rule('/pictures/<int:picture_id>', defaults={'size': u'full'}, endpoint='pictures.picture'),
    Rule('/pictures/<int:picture_id>/<size>', endpoint='pictures.picture'),
    Rule('/mail/', endpoint='mail.inbox'),
    Rule('/mail/.rss', endpoint='mail.inbox_rss'),
    Rule('/mail/send', endpoint='mail.send'),
    Rule('/mail/<int:conversation_id>', endpoint='mail.conversation'),
    Rule('/mail/<int:conversation_id>/reply', endpoint='mail.reply'),
    Rule('/mail/delete', endpoint='mail.multi_delete'),
    Rule('/json/pre_mail_message', endpoint='mail.pre_mail_message_json'),
    Rule('/pets/imades/<int:species_id>/<int:appearance_id>/<color:color>', endpoint='pets.pet_image'),
    Rule('/pets/create/<int:species_id>', 'pets.create_pet'),
    Rule('/pets/', endpoint='pets.pet_list'),
    Rule('/pets/create/', endpoint='pets.species_list'),
    Rule('/groups/', endpoint='groups'),
    Rule('/groups/<int:group_id>', endpoint='groups.group'),
    Rule('/groups/list', endpoint='groups.group_list'),
    Rule('/static/<path:f>', endpoint='static', build_only=True),
    Rule('/urls.js', endpoint='urls.urls_js')
], charset='utf-8', converters={'color': ColorConverter})

def urls_js(req):
    last_modified = datetime.utcfromtimestamp(stat(__file__).st_mtime)
    js = 'var url_map = %s;' % urls.generate_javascript(None)
    response = Response(js, mimetype='text/javascript')
    response.headers['Last-Modified'] = http_date(last_modified)
    return response