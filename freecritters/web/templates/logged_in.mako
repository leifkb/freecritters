<%inherit file="layout.mako"/>\
<%def name="title()">Logged in</%def>\
<p>Welcome back, ${fc.req.user.username}! You've been logged in. Would you like to visit the <a href="${fc.url('home')}">home page</a>?</p>