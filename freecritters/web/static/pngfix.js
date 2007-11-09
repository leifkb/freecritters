/*

Fix for PNGs in IE 6. Partially based on a script from:
http://homepage.ntlworld.com/bobosola.

*/

var arVersion = navigator.appVersion.split("MSIE");
var version = parseFloat(arVersion[1]);

function fixPNG (myImage, cloneIfNotIe) {
    if (version >= 5.5 && version < 7 && document.body.filters) {
        var node = document.createElement('span');
        node.id = myImage.id;
        node.className = myImage.className;
        node.title = myImage.title;
        node.style.cssText = myImage.style.cssText;
        node.style.setAttribute('filter', "progid:DXImageTransform.Microsoft.AlphaImageLoader"
                                        + "(src=\'" + myImage.src + "\', sizingMethod='scale')");
        node.style.fontSize = '0';
        node.style.width = myImage.width.toString() + 'px';
        node.style.height = myImage.height.toString() + 'px';
        node.style.display = 'inline-block';
        return node;
    } else {
        if (cloneIfNotIe || cloneIfNotIe == undefined) {
            myImage = myImage.cloneNode(false);
        }
        return myImage;
    }
};

addLoadEvent(function() {
    if (version >= 5.5 && version < 7 && document.body.filters) {
        var images = document.images;
        for (var i = images.length-1; i >= 0; i--) {
            var img = images[i];
            swapDOM(img, fixPNG(img));
        }
    }
});