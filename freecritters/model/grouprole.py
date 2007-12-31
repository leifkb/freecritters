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
            return bool(self.standard_permissions.filter_by(
                standard_group_permission_id=permission.standard_group_permission_id
            ).count())
        elif isinstance(permission, SpecialGroupPermission):
            return bool(self.special_permissions.filter_by(
                special_group_permission_id=permission.special_group_permission_id
            ).count())
        elif permission is None:
            return True
        else:
            assert False