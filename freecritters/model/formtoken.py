from freecritters.model.tables import form_tokens
from sqlalchemy import and_
from datetime import datetime, timedelta
from freecritters.model.session import Session
import uuid

class FormToken(object):
    def __init__(self, user, subaccount=None):
        self.user = user
        self.subaccount = subaccount
        self.token = unicode(uuid.uuid4())
        self.creation_time = datetime.utcnow()
    
    @classmethod
    def form_token_for(cls, user, subaccount=None):
        """Finds or creates a form token for a user and subaccount and returns
        it.
        """
        
        min_creation_time = datetime.utcnow() - timedelta(days=1)
        form_token = cls.query.filter(and_(
            form_tokens.c.user_id==user.user_id,
            form_tokens.c.subaccount_id==(subaccount and subaccount.subaccount_id),
            form_tokens.c.creation_time>=min_creation_time
        )).first()
        if form_token is None:
            form_token = cls(user, subaccount)
        return form_token
    
    @classmethod
    def find_form_token(cls, token, user, subaccount=None):
        """Finds an existing form token, or returns None if it doesn't
        exist.
        """
        # Blah, blah, reuse code instead of copying and pasting, blah blah...
        min_creation_time = datetime.utcnow() - timedelta(days=7)
        form_token = cls.query.filter(and_(
            form_tokens.c.user_id==user.user_id,
            form_tokens.c.subaccount_id==(subaccount and subaccount.subaccount_id),
            form_tokens.c.creation_time>=min_creation_time,
            form_tokens.c.token==token
        )).first()
        return form_token