class StandardGroupPermission(object):
    def __init__(self, label, title, description):
        self.label = label
        self.title = title
        self.description = description
    
    @classmethod
    def find_label(cls, label, allow_none=False):
        result = cls.query.filter_by(label=label).first()
        if not allow_none:
            assert result is not None, \
                'Group permission labelled %r not found.' % label
        return result