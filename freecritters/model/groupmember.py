from datetime import datetime

class GroupMember(object):
    def __init__(self, user, group, group_role):
        assert group_role.group == group
        self.user = user
        self.group = group
        self.group_role = group_role
        self.joined = datetime.utcnow()
    
    def has_permission(self, permission):
        if self.user == self.group.owner:
            return True
        else:
            return self.group_role.has_permission(permission)