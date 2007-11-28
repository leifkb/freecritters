from freecritters.model.tables import species, appearances, species_appearances
from sqlalchemy import func, and_

class Species(object):               
    def __init__(self, name, creatable=True):
        self.name = name
        self.creatable = creatable
    
    @property
    def can_be_created(self):
        if not self.creatable:
            return False
        return bool(self.appearances.filter(creatable=True)[:1].count())
    
    @classmethod
    def find_creatable(cls):
        return cls.query.filter(and_(
            species.c.creatable==True,
            species_appearances.c.species_id==species.c.species_id,
            species_appearances.c.appearance_id==appearances.c.appearance_id,
            appearances.c.creatable==True,
        )).group_by(list(species.c))