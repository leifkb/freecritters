<%inherit file="layout.mako"/>\
<%def name="tabs()"><%
    return [
        Tab('Pets', 'pets.pet_list'),
        Tab('Create pet', 'pets.species_list')
    ]
%></%def>\
${next.body()}