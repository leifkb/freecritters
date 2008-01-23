function setCaretToEnd(element) {
    var pos = element.value.length;
    if (element.createTextRange) {
        var range = element.createTextRange();
        range.moveStart('character', pos);
        range.select();
    } else if (element.setSelectionRange) {
        element.setSelectionRange(pos, pos);
    }
}

function makePostRequest(url, data) {
    var form = document.createElement('form');
    form.style.display = 'none';
    document.body.appendChild(form);
    form.method = 'post';
    form.action = url;
    /* input can't go directly inside form in strict */
    var formDiv = document.createElement('div');
    form.appendChild(formDiv);
    for (var key in data) {
        if (typeof(data[key]) !== 'function') {
            var field = document.createElement('input');
            field.type = 'hidden';
            field.name = key;
            field.value = data[key].toString();
            formDiv.appendChild(field);
        }
    }
    form.submit();
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
            if (!getElementsByTagAndClassName('td', 'dedicatedtolink', row).length) continue;
            connect(row, 'onmouseover', function(e) {
                addElementClass(e.src(), 'hoveredrow');
            });
            connect(row, 'onmouseout', function(e) {
                removeElementClass(e.src(), 'hoveredrow');
            });
        }
    }
});

addLoadEvent(function() {
    if (form_token === null) {
        return;
    }
    var links = getElementsByTagAndClassName('a', 'confirm');
    for (var i = 0; i < links.length; i++) {
        var link = links[i];
        connect(link, 'onclick', function(e) {
            if (confirm('Are you sure you want to do that?')) {
                makePostRequest(this.href, {'form_token': form_token});
            }
            e.preventDefault();
        });
    }
});