<%inherit file="pet_layout.mako"/>\
<%def name="title()">Creating a pet</%def>\

<p>Please choose a species:</p>
<table class="petlist">
    % for i, (species, appearance, color) in enumerate(items):
<%  link = fc.url('pets.create_pet', species_id=species.species_id) %>\
<%  image = fc.url('pets.pet_image', species_id=species.species_id, appearance_id=appearance.appearance_id, color=color) %>\
    <tr\
% if i == len(items) - 1:
 class="last"\
% endif
>
        <td class="petlist_petimage"><a href="${link}"><img src="${image}" alt=""></a></td>
        <td class="petlist_petinfo">
            <h3><a href="${link}">${species.name}</a></h3>
        </td>
    </tr>
    % endfor
</table>