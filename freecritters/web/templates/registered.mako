<%inherit file="layout.mako"/>\
<%def name="title()">Registered</%def>\

<p>Welcome to ${fc.req.config.site.name}, ${fc.req.user.username}. You've been registered and logged in. Would you like to visit the <a href="${fc.url('home')}">home page</a>?</p>