<%inherit file="layout.mako"/>\
<%def name="title()">${user.username}'s profile</%def>\

% if pet_count:
<div class="profilerandompet">
    <h3>\
% if pet_count > 1:
Random pet\
% else:
Pet\
% endif
</h3>
    <div class="profilerandompetmore dedicatedtolink"><a href="#">(${pet_count-1} more pets)</a></div>
    <div class="profilerandompetimage"><img src="${fc.url('pets.pet_image', species_id=pet.species.species_id, appearance_id=pet.appearance.appearance_id, color=pet.color)}" alt=""></div>
    <div class="profilerandompetname">${pet.name}</div>
</div>
% endif

% if groups:
<table class="normal minigrouplist profilegrouplist">
    <caption>Groups</caption>
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

<table class="labels">
    <tbody>
        <tr>
            <th>Registered:</th>
            <td>${datetime(user.registration_date)}</td>
        </tr>
        <tr>
            <th>Role:</th>
            <td>${user.role.name}</td>
        </tr>
    </tbody>
</table>

${user.rendered_profile|n}