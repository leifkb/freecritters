from datetime import datetime
from freecritters.textformats import render_html

class Post(object):
    def __init__(self, thread, user, message, rendered_message=None):
        if rendered_message is None:
            rendered_message = render_html(message)
        self.thread = thread
        self.user = user
        self.message = message
        self.rendered_message = rendered_message
        self.created = datetime.utcnow()
        thread.last_post = datetime.utcnow()