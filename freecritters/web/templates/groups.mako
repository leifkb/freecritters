<%inherit file="groups_layout.mako"/>\
<%namespace file="formsuccess.mako" import="formsuccess"/>\
<%def name="title()">Groups</%def>\

${formsuccess(
    left=u'Left group.',
    deleted=u'Deleted group.'
)}

% if groups:
<table class="normal" id="yourgroups">
    <caption>Your groups</caption>
    <thead>
        <tr>
            <th>Name</th>
            <th>Type</th>
        </tr>
    </thead>
    <tbody>
    % for group in groups:
        <tr>
            <td class="groupnamecol dedicatedtolink"><a href="${fc.url('groups.group', group_id=group.group_id)}">${group.name}</a></td>
            <td class="grouptypecol">${group.type_name}</td>
        </tr>
    % endfor
    </tbody>
</table>
% endif

<p>Groups are private communities, formed by users. You can create your own group,
or you can join one founded by someone else.<p>

<p>There are three different types of group:</p>

<ul>
    <li><strong>Clubs</strong>, whose members can join guilds and other clubs.</li>
    <li><strong>Guilds</strong>, whose members can join clubs, but not other guilds.</li>
    <li><strong>Cults</strong>, whose members can be in no other group.</li>
</ul>