# -*- coding: utf-8 -*-

from sqlalchemy import DynamicMetaData, Table, Column, Integer, Unicode, mapper

metadata = DynamicMetaData()

messages = Table('messaes', metadata,
    Column('message_id', Integer, primary_key=True),
    Column('message', Unicode())
)

class Message(object):
    def __repr__(self):
        return "%s(%r)" % \
            (self.__class__.__name__, self.message)
    
    def __unicode__(self):
        return self.message

message_mapper = mapper(Message, messages)
