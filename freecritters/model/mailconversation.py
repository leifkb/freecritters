class MailConversation(object):
    def __init__(self, subject):
        self.subject = subject
        self.creation_time = datetime.utcnow()