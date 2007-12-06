<%inherit file="layout.mako"/>\
<%def name="title()">${user.username}'s profile</%def>\

<p><em>Registered ${datetime(user.registration_date)}.</em></p>
${user.rendered_profile|n}