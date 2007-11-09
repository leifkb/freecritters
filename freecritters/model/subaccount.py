from freecritters.model.util import PasswordHolder

class Subaccount(PasswordHolder):          
    def __init__(self, user, name, password):
        super(Subaccount, self).__init__()
        self.user = user
        self.name = name
        self.change_password(password)