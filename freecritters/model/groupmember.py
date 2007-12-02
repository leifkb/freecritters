from datetime import datetime

class GroupMember(object):
    def __init__(self, user, group, group_role):
        assert group_role.group == group
        self.user = user
        self.group = group
        self.group_role = group_role
        self.joined = datetime.utcnow()