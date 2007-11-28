from freecritters.model.session import Session
from freecritters.model.tables import mail_participants
from datetime import datetime

class MailParticipant(object):    
    def __init__(self, conversation, user, system=False):
        self.conversation = conversation
        self.user = user
        self.last_change = datetime.utcnow()
        self.last_view = None
        self.deleted = False
        self.system = system

    def delete(self):
        self.deleted = True
        for participant in self.conversation.participants:
            if not participant.deleted:
                break
        else:
            Session.delete(self.conversation)
    
    @property
    def is_new(self):
        return self.last_view is None or self.last_change > self.last_view

    @classmethod
    def find(cls, user, user2=None, system=None):
        result = cls.query.filter_by(user_id=user.user_id, deleted=False)
        if system is not None:
            result = result.filter_by(system=system)
        if user2 is not None:
            mp2 = mail_participants.alias()
            result = result.filter(
                mp2.conversation_id==mail_participants.conversation_id,
                mp2.user_id==user2.user_id
            )
        return result