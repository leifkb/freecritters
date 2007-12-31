class Forum(object):
    def __init__(self, name, group=None):
        self.name = name
        self.group = group
        self.thread_count = 0