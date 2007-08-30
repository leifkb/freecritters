addLoadEvent(function(ev) {
    removeElement('preview');
    var handle = null;
    var image;
    var change = function(ev) {
        if (handle) {
            handle.cancel();
        }
        handle = callLater(0.25, function() {
            handle = null;
            var color = $('color').value.replace('#', '');
            var appearance_id = initial_appearance_id;
            if ($('appearance')) {
                appearance_id = $('appearance').value;
            }
            var url = '/pets/images/' + species_id + '/' + appearance_id + '/' + color + '.png';
            image = new Image();
            image.id = 'petpreviewimg';
            connect(image, 'onload', function(ev) {
                swapDOM($('petpreviewimg'), fixPNG(image, false));
            });
            image.src = url;
        });
    };
    connect('color', 'onchange', change);
    if ($('appearance')) {
        connect('appearance', 'onchange', change);
    }
});