import re

class Group(object):
    name_length = 30
    name_regex = re.compile(
        ur'^(?=.{1,%s}$)[ _-]*[A-Za-z][A-Za-z0-9 _-]*$' % name_length)
    
    def __init__(self, type, name, description, owner):
        self.type = type
        self.name = name
        self.description = description
        self.owner = owner
        self.member_count = 0
        self.default_role = GroupRole(self, u'Member')
        admin_role = GroupRole(self, u'Administrator')
        GroupMember(self, owner, admin_role)
        self.created = datetime.utcnow()
    
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
    def find_group(cls, name):
        """Finds a group by name or (stringified) group ID. Returns None if
        the group doesn't exist.
        """
        if name.isdigit():
            return cls.query.get(int(name))
        else:
            name = cls.unformat_name(name)
            return cls.filter_by(unformatted_name=name).one()
    
    @classmethod
    def types_can_coexist(cls, type1, type2):
        if type1 is None or type2 is None:
            return True
        if type1 > type2:
            type1, type2 = type2, type1
        if type2 == 2:
            return False
        if type1 == type2 == 1:
            return False
        return True
    
    def can_coexist_with(self, other_type):
        return self.types_can_coexist(self.type, other_type)
    
    @property
    def type_name(self):
        return self.type_names[self.type]