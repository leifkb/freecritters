<%inherit file="settings_layout.mako"/>\
<%namespace file="formsuccess.mako" import="formsuccess"/>\
<%namespace file="form.mako" import="render_form"/>\
<%def name="title()">Changing password</%def>\

${formsuccess(changed=u'Password changed.')}

${render_form(form)}