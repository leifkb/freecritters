# -*- coding: utf-8 -*-

from freecritters.model import Picture
from freecritters.web.application import Response

sizes = {
    'full': None,
    'thumb': (120, 120)
}

def picture(req, picture_id, size='full'):  
    try:
        size = sizes[size]
    except KeyError:
        return None
        
    picture = Picture.query.get(int(picture_id))
    if picture is None:
        return None
    
    req.check_modified(picture.last_change)
    
    if size is None:
        image = str(picture.image)
    else:
        image = str(picture.resized_within(*size).image)
        
    return Response(image, mimetype=picture.mime_type) \
           .last_modified(picture.last_change)