from datetime import datetime
from freecritters.textformats import render_html

class MailMessage(object):
    def __init__(self, conversation, user, message, rendered_message=None):
        self.conversation = conversation
        self.user = user
        self.message = message
        if rendered_message is None:
            rendered_message = render_html(message)
        self.rendered_message = rendered_message
        self.sent = datetime.utcnow()