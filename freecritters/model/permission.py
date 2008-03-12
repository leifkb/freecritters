class Permission(object):
    def __init__(self, title, description, label=None):
        self.title = title
        self.description = description
        self.label = label
        
    @classmethod
    def find_label(cls, label, allow_none=False):
        result = cls.query.filter_by(label=label).first()
        if not allow_none:
            assert result is not None, \
                'Permission labelled %r not found.' % label
        return result
    
    def possessed_by(self, user, subaccount=None):
        """Checks whether this permission is possessed by a given user and,
        optionally, subaccount.
        """
        
        return self in user.role.permissions and (subaccount is None or self in subaccount.permissions)