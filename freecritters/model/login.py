class Login(object):
    def __init__(self, user, subaccount=None):
        self.user = user
        self.subaccount = subaccount
        self.code = unicode(uuid.uuid4())
        self.creation_time = datetime.utcnow()