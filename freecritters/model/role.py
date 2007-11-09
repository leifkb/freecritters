class Role(object):             
    def __init__(self, name, label=None):
        self.label = label
        self.name = name
    
    @classmethod
    def find_label(cls, label, allow_none=False):
        result = cls.query.filter_by(label=label).one()
        if not allow_none:
            assert result is not None, 'Role labelled %r not found.' % label
        return result