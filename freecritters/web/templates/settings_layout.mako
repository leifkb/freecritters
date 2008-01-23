<%inherit file="layout.mako"/>\
<%def name="tabs()"><%
return [
    Tab(u'Profile', 'settings.edit_profile'),
    Tab(u'Change password', 'settings.change_password'),
    Tab(u'Subaccounts', 'settings.subaccount_list'),
    Tab(u'Create subaccount', 'settings.create_subaccount')
]
%></%def>\
${next.body()}