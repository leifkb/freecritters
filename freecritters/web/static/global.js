function setCaretToEnd (element) {
    var pos = element.value.length;
    if (element.createTextRange) {
        var range = element.createTextRange();
        range.moveStart('character', pos);
        range.select();
    } else if (element.setSelectionRange) {
        element.setSelectionRange(pos, pos);
    }
}

function quote(field_id, message) {
    window.location.hash = field_id;
    var field = $(field_id);
    field.value += "<blockquote>" + message + "</blockquote>\n";
    field.focus();
    setCaretToEnd(field);
}
