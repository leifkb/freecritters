import re
from datetime import datetime

class Pet(object):
    name_length = 20
    name_regex = re.compile(
        ur'^(?=.{1,%s}$)[ _-]*[A-Za-z][A-Za-z0-9 _-]*$' % name_length)
    
    def __init__(self, name, user, species, appearance, color):
        self.species_appearance = species.species_appearances.filter_by(
            appearance_id=appearance.appearance_id
        ).first()
        self.created = datetime.utcnow()
        self.change_name(name)
        self.user = user
        self.color = color
        
    _unformat_name_regex = re.compile(ur'[^a-zA-Z0-9]+')
    @classmethod
    def unformat_name(self, name):
        """Removes formatting from a name."""
        name = self._unformat_name_regex.sub(u'', name)
        name = name.lower()
        return name
    
    def change_name(self, name):
        self.name = name
        self.unformatted_name = self.unformat_name(name)
    
    @classmethod
    def find_pet(cls, name):
        """Finds a pet by name or (stringified) pet ID. Returns None if
        the pet doesn't exist.
        """
        if name.isdigit():
            return cls.query.get(int(name))
        else:
            name = cls.unformat_name(name)
            return cls.query.filter_by(unformatted_name=name).first()
    
    def _set_color(self, color):
        self.color_red, self.color_green, self.color_blue = color
    
    def _get_color(self):
        return self.color_red, self.color_green, self.color_blue
    
    color = property(_get_color, _set_color)
    
    def _set_species(self, species):
        self.species_appearance = species.species_appearances.filter_by(
            appearance_id=self.appearance.appearance_id
        ).first()
    
    def _get_species(self):
        return self.species_appearance.species
    
    species = property(_get_species, _set_species)
    
    def _set_appearance(self, appearance):
        self.species_appearance = appearance.species_appearances.filter_by(
            species_id=self.species.species_id
        ).first()
    
    def _get_appearance(self):
        return self.species_appearance.appearance
    
    appearance = property(_get_appearance, _set_appearance)
    