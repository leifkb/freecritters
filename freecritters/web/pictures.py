# -*- coding: utf-8 -*-

from freecritters.model import ctx, Picture
from freecritters.web.application import FreeCrittersResponse
from colubrid.exceptions import PageNotFound, AccessDenied

sizes = {
    'full': None,
    'thumb': (120, 120)
}

def picture(req, picture_id, size='full'):  
    try:
        size = sizes[size]
    except KeyError:
        raise PageNotFound()
        
    picture = Picture.get(int(picture_id))
    if picture is None:
        raise PageNotFound()
        
    if size is None:
        image = picture.image
    else:
        image = picture.resized_within(*size).image
        
    return FreeCrittersResponse(
        image,
        [('Content-Type', picture.mime_type)]
    )