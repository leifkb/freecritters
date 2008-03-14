from freecritters.model.session import Session
from sqlalchemy import asc, desc

class Forum(object):
    def __init__(self, name, group=None):
        self.name = name
        self.group = group
        self.thread_count = 0
    
    @property
    def siblings(self):
        if self.group is None:
            return Forum.query.filter_by(group_id=None)
        else:
            return self.group.forums
    
    def swap_with(self, other):
        if other is None:
            return
        assert self.group == other.group
        
        other_order_num = other.order_num
        my_order_num = self.order_num
        other.order_num = None
        self.order_num = None
        Session.flush()
        other.order_num = my_order_num
        self.order_num = other_order_num
    
    def move_up(self):
        other = self.siblings.filter(Forum.order_num < self.order_num).order_by(desc(Forum.order_num)).first()
        self.swap_with(other)
    
    def move_down(self):
        other = self.siblings.filter(Forum.order_num > self.order_num).order_by(asc(Forum.order_num)).first()
        self.swap_with(other)