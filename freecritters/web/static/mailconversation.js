function findMessageContainer(message_id) {
    return $('mailmessage' + message_id);
}

function findMessageHeader(message_id) {
    return getFirstElementByTagAndClassName('p', 'mailmessageheader', findMessageContainer(message_id));
}

function addToggliness(message_id) {
    var header = findMessageHeader(message_id);
    var container = findMessageContainer(message_id);
    connect(header, 'onclick', function(ev) {
        if (ev.target() != ev.src()) {
            // This stops clicks on e.g. the 'quote' link from toggling visibility.
            return;
        }
        if (hasElementClass(container, 'collapsed')) {
            removeElementClass(container, 'collapsed');
            addElementClass(container, 'expanded');
        } else {
            removeElementClass(container, 'expanded');
            addElementClass(container, 'collapsed');
        }
    });
}

addLoadEvent(function() {
    for (var i=0; i < collapsed.length; i++) {
        if (window.location.hash == '#mailmessage' + collapsed[i]) {
            addElementClass(findMessageContainer(collapsed[i]), 'expanded');
        } else {
            addElementClass(findMessageContainer(collapsed[i]), 'collapsed');
        }
        addToggliness(collapsed[i]);
    }
    for (var i=0; i < expanded.length; i++) {
        addElementClass(findMessageContainer(expanded[i]), 'expanded');
        addToggliness(expanded[i]);
    }
});