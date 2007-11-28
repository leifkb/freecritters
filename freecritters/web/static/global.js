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

addLoadEvent(function() {
    var elements = getElementsByTagAndClassName(null, 'dedicatedtolink');
    for (var i = 0; i < elements.length; i++) {
        var element = elements[i];
        element.style.cursor = 'pointer';
        (function() {
            var old_status = '';
            var link = getFirstElementByTagAndClassName('a', null, element);
            if (!link) return;
            connect(element, 'onclick', function(e) {
                document.location.href = link.href;
            });
        })();
    }
});

addLoadEvent(function() {
    var tables = getElementsByTagAndClassName('table', 'normal');
    for (var i = 0; i < tables.length; i++) {
        var table = tables[i];
        var tbody = getFirstElementByTagAndClassName('tbody', null, table);
        if (!tbody) tbody = table;
        var rows = getElementsByTagAndClassName('tr', null, tbody);
        for (var j = 0; j < rows.length; j++) {
            var row = rows[j];
            addElementClass(row, j % 2 == 0 ? 'evenrow' : 'oddrow');
            connect(row, 'onmouseover', function(e) {
                addElementClass(e.src(), 'hoveredrow');
            });
            connect(row, 'onmouseout', function(e) {
                log(e.src());
                removeElementClass(e.src(), 'hoveredrow');
            });
        }
    }
});