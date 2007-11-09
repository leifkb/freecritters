class MailMessage(object):
    def __init__(self, conversation, user, message, rendered_message):
        self.conversation = conversation
        self.user = user
        self.message = message
        self.rendered_message = rendered_message
        self.sent = datetime.utcnow()