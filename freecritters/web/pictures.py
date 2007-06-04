# -*- coding: utf-8 -*-

from sqlalchemy import Query, undefer
from freecritters.model import ctx, Picture
from freecritters.web.application import FreeCrittersResponse
from colubrid.exceptions import PageNotFound, AccessDenied

sizes = {
    'full': None,
    'thumb': (120, 120)
}

def picture(req, picture_id, size='full'):
    try:
        picture_id = int(picture_id)
    except ValueError:
        raise PageNotFound()
        
    try:
        size = sizes[size]
    except KeyError:
        raise PageNotFound()
        
    picture = Query(Picture).options(undefer('image')).get(picture_id)
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