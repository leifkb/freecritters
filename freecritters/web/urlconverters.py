from werkzeug.routing import BaseConverter

class ColorConverter(BaseConverter):
    regex = '[0-9A-F]{6}'
    
    def to_python(self, value):
        return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)
    
    def to_url(self, value):
        return '%02X%02X%02X' % value