from datetime import datetime
from sqlalchemy import outerjoin, and_
from freecritters.model.tables import posts, group_members

class Thread(object):
    max_subject_length = 60
    
    def __init__(self, forum, user, subject):
        self.forum = forum
        self.user = user
        self.subject = subject
        self.created = datetime.utcnow()
        self.post_count = 0