function setCaretToEnd (element) {
    if (element.createTextRange) {
        var elval = element.value;
        var elrng = element.createTextRange();
        elrng.moveStart('character', elval.length);
        elrng.select();
    }
}

function quote(field_id, message) {
    window.location.hash = field_id;
    var field = $(field_id);
    field.value += "<blockquote>" + message + "</blockquote>\n";
    field.focus();
    setCaretToEnd(field);
}
