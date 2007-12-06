<%inherit file="../layout.mako"/>\
<%def name="title()">Access denied</%def>\

<p>You're not allowed to perform the action you're trying to. There are a few
possible causes for this problem:</p>
<ul>
    <li>You're trying to use a page that requires you to be logged in, but
    you aren't. (Try <a href="${fc.url('login')}">logging in</a> or
    <a href="${fc.url('register')}register">registering</a>.)</li>
    <li>You're trying to do something like registration or login which
    requires you to be logged out, but you aren't. (Try
    <a href="${fc.url('logout')}">logging out</a>.)</li>
    <li>You're using a subaccount which limits the action you're trying to
    perform.</li>
    <li>You're trying to access something (like mail) that belongs to someone
    else.</li>
    <li>You're trying to use an administration page, but you aren't an
    administrator.</li>
</ul>