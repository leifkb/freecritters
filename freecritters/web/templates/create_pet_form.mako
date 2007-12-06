<%inherit file="pet_layout.mako"/>\
<%namespace file="form.mako" import="render_form_fields, render_form_header, render_form_field"/>\
<%def name="title()">Creating a ${species.name}</%def>\
<%def name="head()">\
<script type="text/javascript">
var species_id = ${species.species_id};
var initial_appearance_id = ${appearance.appearance_id};
</script>
<script src="${fc.url('static', fn='pet_create.js')}" type="text/javascript"></script>
</%def>\

${render_form_header(form)}
<div id="petpreview">
<div><img src="${fc.url('pets.pet_image', species_id=species.species_id, appearance_id=appearance.appearance_id, color=color)}" alt="" id="petpreviewimg"></div>
<div>${render_form_field(form.field_results('preview'))}</div> 
</div>
${render_form_fields(form, ['form_token', 'pet_name', 'color', 'submit'])}
</form>