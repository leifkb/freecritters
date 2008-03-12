<%inherit file="group_layout.mako"/>\
<%namespace file="form.mako" import="render_form"/>\
<%def name="title()">Leaving ${group.name}</%def>\

<p>You can't leave the group ${group.name} because you own it. You must either appoint someone else as this group's owner or delete it.</p>