<%inherit file="pet_layout.mako"/>\
<%namespace file="formsuccess.mako" import="formsuccess"/>\
<%def name="title()">Pets</%def>\

${formsuccess(created=u'Pet created.')}

% if not pets:
<p>You don't have any pets.</p>
% else:
<table class="petlist">
    % for i, pet in enumerate(pets):
    <tr\
% if i == len(pets) - 1:
 class="last"\
% endif
>
        <td class="petlist_petimage"><img src="${fc.url('pets.pet_image', species_id=pet.species.species_id, appearance_id=pet.appearance.appearance_id, color=pet.color)}" alt=""></td>
        <td class="petlist_petinfo">
            <h3>${pet.name}</h3>
            <div><strong>Species:</strong> ${pet.species.name}</div>
            <div><strong>Appearance:</strong> ${pet.appearance.name}</div>
            <div><strong>Color:</strong> ${"#%02X%02X%02X" % pet.color}</div>
        </td>
    </tr>
    % endfor
</table>
% endif