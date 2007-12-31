import re
from freecritters.textformats import render_plain_text
from freecritters.model.session import Session
from datetime import datetime

class Group(object):
    name_length = 30
    name_regex = re.compile(
        ur'^(?=.{1,%s}$)[ _-]*[A-Za-z][A-Za-z0-9 _-]*$' % name_length)
    max_description_length = 500
    type_names = [u'Club', u'Guild', u'Cult']

    def __init__(self, type, name, description, owner):
        from freecritters.model.groupmember import GroupMember
        from freecritters.model.grouprole import GroupRole
        from freecritters.model.standardgrouppermission import StandardGroupPermission
        standard_permissions = StandardGroupPermission.query.all()
        self.type = type
        self.change_name(name)
        self.description = description
        self.home_page = home_page
        self.rendered_home_page = rendered_home_page
        self.owner = owner
        self.member_count = 0
        self.created = datetime.utcnow()
        admin_role = GroupRole(self, u'Administrator')
        for permission in standard_permissions:
            admin_role.standard_permissions.append(permission)
        default_role = GroupRole(self, u'Member')
        default_role.is_default = True
        GroupMember(owner, self, admin_role)
        
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
            return cls.query.filter_by(unformatted_name=name).first()
    
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
    
    @property
    def rendered_description(self):
        return render_plain_text(self.description, 5)
    
    @property
    def default_role(self):
        return self.roles.filter_by(is_default=True).one()