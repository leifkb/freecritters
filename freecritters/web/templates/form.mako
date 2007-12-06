<%def name="render_form_field(field_results)">\
<% field = field_results.field %>\
<% full_id = field_results.form_results.form.id_prefix + field.id_ %>\
% if field.type_name in ("TextField", "PasswordField", "ColorSelector"):
<input type=\
% if field.type_name == "PasswordField":
"password"\
% else:
"text"\
% endif
 name="${field.name}"\
% if field.type_name == "ColorSelector":
 class="color"\
% endif
% if field_results.has_value:
 value="${field_results.value}"\
% endif
 id="${full_id}"\
% if field.size is not None:
 size="${field.size}"\
% endif
% if field.max_length is not None:
 maxlength="${field.max_length}"\
% endif
>\
% elif field.type_name == "CheckBox":
<input type="checkbox" name="${field.name}"\
% if field_results.has_value and field_results.value:
 checked="checked"\
% endif
 id="${full_id}" value="${field.value}">\
% elif field.type_name == 'TextArea':
<textarea name="${field.name}" id="${full_id}" rows="${field.rows}" cols="${field.cols}">
% if field_results.has_value:
${field_results.value}\
% endif
</textarea>\
% elif field.type_name == 'SelectMenu':
<select name="${field.name}" id="${full_id}">
% for value, caption in field.options:
<option value="${value}"\
% if field_results.has_value and value == field_results.value:
 selected="selected"\
 % endif
>${caption}</option>\
% endfor
</select>\
% elif field.type_name == 'HiddenField':
<input type="hidden" name="${field.name}" id="${full_id}"\
% if field_results.has_value:
 value="${field_results.value}"\
% endif
>\
% elif field.type_name == 'SubmitButton':
<input type="submit" name="${field.name}" id="${full_id}" value="${field.title}">\
% endif
</%def>

<%def name="render_form_start_tag(form_results)">\
<form action="${form_results.action_url}" method="${form_results.form.method}">\
</%def>

<%def name="render_form_error_warning(form_results)">\
% if form_results.has_errors:
<p class="formhaserrors"><strong>Your form submission has errors. Please review and correct them.</strong></p>\
% endif
</%def>

<%def name="render_form_header(form_results)">\
${render_form_start_tag(form_results)}
${render_form_error_warning(form_results)}\
</%def>

<%def name="render_form_fields(form_results, fields=None)">\
<%
    if fields is None:
        fields = list(form_results.form)
%>\
<div class="formfields">
% for index, field in enumerate(fields):
<%
    try:
        field = form_results.form.field(field)
    except KeyError:
        continue
    field_results = form_results.field_results(field)
%>\
<div class="\
% if index == len(fields) - 1:
last \
% endif
${field.type_name}\
% if field.type_name == 'HiddenField' and field_results.error is None:
 hidden\
% endif
 formfield">
% if field.type_name not in ('HiddenField', 'SubmitButton'):
<div class="formfieldtitle"><label for="${form_results.form.id_prefix}${field.id_}">${field.title}:</label></div>
% endif
<div class="formfieldcontrol">${render_form_field(field_results)}</div>
% if field_results.error is not None:
<div class="formfielderror"><em>${field_results.error}</em></div>
% elif field.description is not None:
<div class="formfielddesc">${field.description}</div>
% endif
<div class="formclearhack">&nbsp;</div>
</div>
% endfor
</div>
</%def>

<%def name="render_form(form_results, fields=None)">\
${render_form_header(form_results)}
${render_form_fields(form_results, fields)}
</form>\
</%def>