from datetime import datetime

class MailConversation(object):
    max_subject_length = 45
    
    def __init__(self, subject):
        self.subject = subject
        self.creation_time = datetime.utcnow()
    
    def find_participant(self, user):
        for participant in self.participants:
            if participant.user == user:
                return participant