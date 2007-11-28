import Image
from freecritters.model.resizedpicture import ResizedPicture
from StringIO import StringIO
from datetime import datetime

class Picture(object):
    def __init__(self, name, copyright, description, image):
        self.name = name
        self.copyright = copyright
        self.description = description
        self.change_image(image)
        self.added = datetime.utcnow()        
    
    def change_image(self, image):
        """Changes the image. Argument can be a PIL image, a file-like object
        containing image data, or a byte string containing image data."""
        if isinstance(image, Image.Image):
            pil_image = image
            image = None
        elif isinstance(image, str):
            pil_image = Image.open(StringIO(image))
        else:
            image = image.read()
            pil_image = Image.open(StringIO(image))
        format = pil_image.format
        if format not in ('PNG', 'JPEG'):
            image = None
            format = 'PNG'
        if image is None:
            image = StringIO()
            pil_image.save(image, format)
            image = image.getvalue()
        self.width, self.height = pil_image.size
        self.format = format
        self.image = image
        self.last_change = datetime.utcnow()
    
    _mime_types = {
        'PNG': 'image/png',
        'JPEG': 'image/jpeg'
    }
    
    @property
    def mime_type(self):
        try:
            return self._mime_types[self.format]
        except KeyError:
            raise AssertionError("Unknown format %r." % self.format)
    
    _extensions = {
        'PNG': '.png',
        'JPEG': '.jpeg'
    }
    
    @property
    def extension(self):
        try:
            return self._extensions[self.format]
        except KeyError:
            raise AssertionError("Unknown format %r." % self.format)
    
    @property
    def pil_image(self):
        data = StringIO(self.image)
        return Image.open(data)
    
    def resized_within(self, width, height):
        """Like resized_to, but the resulting image will fit within the
        dimensions while preserving its aspect ration.
        """
        if width > self.width and height > self.height:
            return self
        if self.width > width:
            new_height = int(round(max(self.height * width / float(self.width), 1.0)))
            new_width = width
        else:
            new_width = int(round(max(self.width * height / float(self.height), 1.0)))
            new_height = height
        return self.resized_to(new_width, new_height)
    
    def resized_to(self, width, height):
        """Resizes the picture to the given dimensions. Returns a ResizedPicture,
        or self if the dimensions are the same.
        """
        if width == self.width and height == self.height:
            return self
        picture = self.resized_pictures.filter_by(width=width, height=height).first()
        if picture is None:
            picture = ResizedPicture(self, width, height)
        return picture