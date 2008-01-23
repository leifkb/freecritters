<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html lang="en">
    <head>
        <title>${self.title()} on ${fc.config.site.name}</title>
        <link rel="stylesheet" media="screen,projection" type="text/css"
              href="${fc.url('static', fn='style.css')}">
        <script src="${fc.url('urls.urls_js')}" type="text/javascript"></script>
        <script type="text/javascript">${fc.req.url_routing_js|n}</script>
        <script type="text/javascript">var form_token = \
% if fc.req.user is not None:
"${fc.req.form_token()}"\
% else:
null\
% endif
;</script>
        <script src="${fc.url('static', fn='MochiKit.js')}" type="text/javascript"></script>
        <!--[if lt IE 7]>
        <script type="text/javascript">IE7_PNG_SUFFIX = "";</script>
        <script src="${fc.url('static', fn='ie7-standard-p.js')}" type="text/javascript"></script>
        <![endif]-->
        <script src="${fc.url('static', fn='pngfix.js')}" type="text/javascript"></script>
        <script src="${fc.url('static', fn='colorselector.js')}" type="text/javascript"></script>
        <script src="${fc.url('static', fn='global.js')}" type="text/javascript"></script>
        ${self.head()}
    </head>
    <body>
        <div id="header">
            <h1><img src="${fc.url('static', fn='logo.png')}" alt="${fc.config.site.name}"></h1>

            <div id="logininfo">
                % if fc.req.user is None:
                <div>Not logged in.</div>
                <div><a href="${fc.url('login')}">Log in</a> or <a href="${fc.url('register')}">Register</a></div>
                % else:
                <div>Logged in as <a href="${fc.url('profile', username=fc.req.user.unformatted_username)}">${fc.req.user.username}</a>\
                    % if fc.req.subaccount is not None:
 (${fc.req.subaccount.name})\
                    % endif
, &curren;${integer(fc.req.user.money)}</div>
                <div><a href="${fc.url('logout')}" class="confirm">Log out</a>, <a href="${fc.url('settings.edit_profile')}">preferences</a></div>
                % endif
            </div>

            <div class="clearhack">&nbsp;</div>
        </div>
        <div id="navs">
            <div class="nav" id="primarynav"><ul>\
<li><a href="${fc.url('home')}">Home</a></li>\
<li><a href="${fc.url('mail.inbox')}">\
<%              has_new_mail = fc.req.user is not None and fc.req.user.has_new_mail %>\
                % if has_new_mail:
<strong class="navnewmail">\
                % endif
Mail\
                % if has_new_mail:
</strong>\
                % endif
</a></li>\
<li><a href="${fc.url('pets.pet_list')}">Pets</a></li>\
<li><a href="${fc.url('forums')}">Forums</a></li>\
<li><a href="${fc.url('groups')}">Groups</a></li>\
</ul></div>
            ${self.secondarynav()}
        </div>
        <div id="main">
            <h2 id="contenttitle">${self.title()}</h2>
<% tabs = self.tabs() %>\
            % if tabs is not None:
            ${self.render_tabs(tabs)}
            % endif
            <div id="content">
                ${next.body()}
            </div>
        </div>
    </body>
</html>\
<%def name="head()"/>\
<%def name="secondarynav()"/>\
<%def name="tabs()"><% return None %></%def>\
<%def name="active_tab()"><% return fc.req.endpoint %></%def>\
<%def name="render_tabs(tabs)">\
<% active = self.active_tab() %>\
<ul class="tabs">\
    % for index, tab in enumerate(tabs):
<li class="\
% if index == len(tabs)-1:
last \
% endif
% if tab.identity == active:
active\
% endif
"><a href="${fc.url(tab.endpoint, **tab.args)}">${tab.text}</a></li>\
    % endfor
</ul>\
</%def>