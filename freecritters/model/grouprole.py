from freecritters.model.standardgrouppermission import StandardGroupPermission
from freecritters.model.specialgrouppermission import SpecialGroupPermission
from freecritters.model.tables import standard_group_permissions, \
                                      special_group_permissions
class GroupRole(object):
    def __init__(self, group, name):
        self.group = group
        self.name = name
        self.is_default = False
        
    def has_permission(self, permission):
        if isinstance(permission, basestring):
            permission = StandardGroupPermission.find_label(permission)
        if isinstance(permission, StandardGroupPermission):
            return permission in self.standard_permissions
        elif isinstance(permission, SpecialGroupPermission):
            return permission in self.special_permissions
        elif permission is None:
            return True
        else:
            assert False