var CROSSHAIRS_LOCATION = '/static/crosshairs.png';
var HUE_SLIDER_LOCATION = '/static/hueslider.png';
var HUE_SLIDER_ARROWS_LOCATION = '/static/huesliderposition.png';
var SAT_VAL_SQUARE_LOCATION = '/static/satvalsquare.png';

var arVersion = navigator.appVersion.split("MSIE");
var version = parseFloat(arVersion[1]);

function trackDrag(node) {
    var lastCoords = null;
    var result = {};
    
    function triggerEvent(ev) {
        var nodeCoords = getElementPosition(node);
        var nodeDimensions = getElementDimensions(node);
        var coords = ev.mouse().page;
        coords.x -= nodeCoords.x;
        coords.y -= nodeCoords.y;
        coords.x = Math.max(0, coords.x);
        coords.y = Math.max(0, coords.y);
        coords.x = Math.min(nodeDimensions.w - 1, coords.x);
        coords.y = Math.min(nodeDimensions.h - 1, coords.y);
        if (coords != lastCoords) {
            signal(result, 'drag', coords);
            lastCoords = coords;
        }
    }
    
    var downIdent;
    function downHandler(ev) {
        triggerEvent(ev);
        disconnect(downIdent);
        var moveIdent = connect(document, 'onmousemove', triggerEvent);
        var upIdent = connect(document, 'onmouseup', function(ev) {
            disconnect(moveIdent);
            disconnect(upIdent);
            downIdent = connect(node, 'onmousedown', downHandler);
        });
    }
    downIdent = connect(node, 'onmousedown', downHandler);
    
    function disableNormalClicking(node) {
        connect(node, 'onmousedown', function(ev) { ev.preventDefault(); });
        connect(node, 'onselectstart', function(ev) { ev.stop(); });
        connect(node, 'ondragstart', function(ev) { ev.stop(); });
        for (var n = node.firstChild; n != null; n = n.nextSibling) {
            disableNormalClicking(n);
        }
    }
    disableNormalClicking(node);
    
    return result;
}

function fireNativeEvent(element, eventName) {
    if (element.fireEvent) {
        element.fireEvent(eventName);
    } else {
        var event = document.createEvent("HTMLEvents");
        event.initEvent(eventName.replace(/^on/, ""), true, true);
        element.dispatchEvent(event);
    }
}

var huePositionImg = document.createElement('img');
huePositionImg.galleryImg = false;
huePositionImg.width = 35;
huePositionImg.height = 11;
huePositionImg.src = HUE_SLIDER_ARROWS_LOCATION;
huePositionImg.style.position = 'absolute';

var hueSelectorImg = document.createElement('img');
hueSelectorImg.galleryImg = false;
hueSelectorImg.width = 35;
hueSelectorImg.height = 200;
hueSelectorImg.src = HUE_SLIDER_LOCATION;
hueSelectorImg.style.display = 'block';

var satValImg = document.createElement('img');
satValImg.galleryImg = false;
satValImg.width = 200;
satValImg.height = 200;
satValImg.src = SAT_VAL_SQUARE_LOCATION;
satValImg.style.display = 'block';

var crossHairsImg = document.createElement('img');
crossHairsImg.galleryImg = false;
crossHairsImg.width = 21;
crossHairsImg.height = 21;
crossHairsImg.src = CROSSHAIRS_LOCATION;
crossHairsImg.style.position = 'absolute';

function makeColorSelector(inputBox) {
    var colorSelectorDiv = DIV();
    colorSelectorDiv.style.padding = '15px';
    colorSelectorDiv.style.position = 'relative';
    colorSelectorDiv.style.height = '275px';
    colorSelectorDiv.style.width = '250px';
    
    if (inputBox == undefined) {
        inputBox = INPUT({'type': 'text', 'class': 'color'});
    } else {
        swapDOM(inputBox, colorSelectorDiv);
    }
    
    var color = Color.fromString(inputBox.value) || Color.redColor();
    var artificialChange = false;
    var hsv = color.asHSV();
    
    var satValDiv = DIV();
    satValDiv.style.position = 'relative';
    satValDiv.style.width = '200px';
    satValDiv.style.height = '200px';
    var newSatValImg = fixPNG(satValImg);
    satValDiv.appendChild(newSatValImg);
    var crossHairs = fixPNG(crossHairsImg);
    satValDiv.appendChild(crossHairs);
    connect(trackDrag(satValDiv), 'drag', function(coords) {
        hsv.s = 1-(coords.y/199);
        hsv.v = coords.x/199;
        color = Color.fromHSV(hsv);
        artificialColorChange = true;
        fireNativeEvent(inputBox, 'onchange');
    });
    colorSelectorDiv.appendChild(satValDiv);
    
    var hueDiv = DIV();
    hueDiv.style.position = 'absolute';
    hueDiv.style.left = '230px';
    hueDiv.style.top = '15px';
    hueDiv.style.width = '35px';
    hueDiv.style.height = '200px';
    var huePos = fixPNG(huePositionImg);
    hueDiv.appendChild(hueSelectorImg.cloneNode(false));
    hueDiv.appendChild(huePos);
    connect(trackDrag(hueDiv), 'drag', function(coords) {
        hsv.h = coords.y/199;
        color = Color.fromHSV(hsv);
        artificialColorChange = true;
        fireNativeEvent(inputBox, 'onchange');
    });
    colorSelectorDiv.appendChild(hueDiv);
    
    var previewDiv = DIV();
    previewDiv.style.height = '50px'
    previewDiv.style.width = '50px';
    previewDiv.style.position = 'absolute';
    previewDiv.style.top = '225px';
    previewDiv.style.left = '15px';
    previewDiv.style.border = '1px solid black';
    colorSelectorDiv.appendChild(previewDiv);
    
    inputBox.size = 8;
    inputBox.style.position = 'absolute';
    inputBox.style.right = '15px';
    colorSelectorDiv.appendChild(inputBox);
    inputBox.style.top = (225 + (25 - (inputBox.offsetHeight/2))).toString() + 'px';
    
    connect(inputBox, 'onchange', function(ev) {
        if (!artificialColorChange) {
            color = Color.fromString(inputBox.value) || Color.blackColor();
            hsv = color.asHSV();
        }
        artificialColorChange = false;
        crossHairs.style.left = Math.round(((hsv.v*199)-10).toString()) + 'px';
        crossHairs.style.top = Math.round((((1-hsv.s)*199)-10).toString()) + 'px';
        huePos.style.top = ((hsv.h*199)-5).toString() + 'px';
        inputBox.value = color.toHexString().toUpperCase();
        previewDiv.style.backgroundColor = color.toHexString();
        satValDiv.style.backgroundColor = Color.fromHSV({h: hsv.h, s: 1.0, v: 1.0}).toHexString();
    });
    artificialColorChange = true;
    fireNativeEvent(inputBox, 'onchange');
}
    
function makeColorSelectors(ev) {
    forEach($$('input.color[type=text]'), makeColorSelector);
}

addLoadEvent(makeColorSelectors);