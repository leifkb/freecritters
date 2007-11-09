from cStringIO import StringIO

class ResizedPicture(object):
    def __init__(self, picture, width, height):
        self.picture = picture
        pil_image = picture.pil_image
            
        if pil_image.mode not in ('RGB', 'RGBA'):
            # Unfortunately, PIL doesn't support generating a palette from an
            # RGBA image, so we can't resize paletted images back into paletted
            # images.
            pil_image = pil_image.convert('RGBA')
            
        pil_image = pil_image.resize((width, height), Image.ANTIALIAS)

        image = StringIO()
        pil_image.save(image, picture.format)
        
        self.image = image.getvalue()
        self.added = datetime.utcnow()
        self.width = width
        self.height = height
        
    @property
    def pil_image(self):
        data = StringIO(self.image)
        return Image.open(data)