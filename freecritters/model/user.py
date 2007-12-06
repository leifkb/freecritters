from freecritters.model.util import PasswordHolder
from freecritters.model.tables import users, mail_participants
from freecritters.model import mailparticipant
from freecritters.textformats import render_plain_text
from sqlalchemy import and_
import re
from datetime import datetime

class User(PasswordHolder):
    username_length = 20
    username_regex = re.compile( # Now I have two problems
        ur'^(?=.{1,%s}$)[ _-]*[A-Za-z][A-Za-z0-9 _-]*$' % username_length)
    pre_mail_message_max_length = 300
    
    def __init__(self, username, password, money=0):
        """Password should be unhashed."""
        
        super(User, self).__init__()
        self.change_username(username)
        self.change_password(password)
        self.money = money
        self.registration_date = datetime.utcnow()
        self.profile = u''
        self.rendered_profile = u''
        self.pre_mail_message = None
        self.last_inbox_view = None
        
    _unformat_username_regex = re.compile(ur'[^a-zA-Z0-9]+')
    @classmethod
    def unformat_username(self, username):
        """Removes formatting from a username."""
        
        username = self._unformat_username_regex.sub(u'', username)
        username = username.lower()
        return username
        
    def change_username(self, username):
        """Changes the username. Also changes the unformatted username and
        validates the new username (ValueError is raised if it's invalid).
        """
        
        if self.username_regex.search(username) is None:
            raise ValueError("Invalid username.")
        self.username = username
        self.unformatted_username = self.unformat_username(username)
        
    @property
    def rendered_pre_mail_message(self):
        if self.pre_mail_message is None:
            return None
        else:
            return render_plain_text(self.pre_mail_message, 3)
    
    @property
    def has_new_mail(self):
        last_mail_change = mailparticipant.MailParticipant.query.filter(and_(
            mail_participants.c.user_id==self.user_id,
            mail_participants.c.deleted==False
        )).max(mail_participants.c.last_change) 
        if last_mail_change is None:
            return False
        else:
            return self.last_inbox_view is None \
                or self.last_inbox_view < last_mail_change
            
    @classmethod
    def find_user(cls, username):
        """Finds a user by username or (stringified) user ID. Returns None if
        the user doesn't exist.
        """
        if username.isdigit():
            return cls.query.get(int(username))
        else:
            username = cls.unformat_username(username)
            return cls.query.filter(users.c.unformatted_username==username).first()
    
    def find_group_membership(self, group):
        return self.group_memberships.filter_by(group_id=group.group_id).first()
    
    @property
    def max_group_type(self):
        from freecritters.model.group import Group
        return self.group_memberships.join('group').max(Group.type)