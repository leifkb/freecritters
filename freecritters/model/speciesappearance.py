import Image

class SpeciesAppearance(object):    
    def __init__(self, species, appearance, white_picture, black_picture):
        self.species = species
        self.appearance = appearance
        self.white_picture = white_picture
        self.black_picture = black_picture
    
    def pil_image_with_color(self, color):
        black_image = self.black_picture.pil_image
        white_image = self.white_picture.pil_image
        if black_image.mode not in ('RGB', 'RGBA'):
            black_image = black_image.convert('RGB')
        if white_image.mode not in ('RGB', 'RGBA'):
            white_image = white_image.convert('RGB')
        if white_image.size != black_image.size:
            white_image = white_image.resize(black_image.size)
        color = [value / 255.0 for value in color]
        if len(color) == 3: # RGB; we want RGBA
            color.append(0.0)
        white_bands = white_image.split()
        black_bands = black_image.split()
        bands = [Image.blend(black_band, white_band, value)
                 for black_band, white_band, value
                     in zip(black_bands, white_bands, color)]
        return Image.merge(min(white_image.mode, black_image.mode), bands)