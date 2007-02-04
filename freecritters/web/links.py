# -*- coding: utf-8 -*-

def user_link(user):
    return u'/users/%s' % user.unformatted_username.encode('ascii')
    
def conversation_link(conversation):
    return u'/mail/%s' % conversation.conversation_id
