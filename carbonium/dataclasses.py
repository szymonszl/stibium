"""This module provides the data classes for Carbonium"""

import attr
from fbchat.models import ThreadType, MessageReaction

@attr.s
class Thread:
    """Class for containing thread's type and id"""
    id_= attr.ib()
    type_ = attr.ib()
    @staticmethod
    def fromkwargs(kwargs): # kwargs are passed as dict
        """Create a Thread class from a handler's kwargs"""
        return Thread(
            id_=str(kwargs.get('thread_id')),
            type_=kwargs.get('thread_type', ThreadType.USER),
        )

@attr.s
class Message:
    """Class for received messages"""
    mid = attr.ib()
    text = attr.ib()
    args = attr.ib(init=False)
    uid = attr.ib()
    thread = attr.ib()
    raw = attr.ib()
    bot = attr.ib()
    def reply(self, text, **kwargs):
        """Send a message to a conversation that the message was received from"""
        return self.bot.send(text, self.thread, **kwargs)

@attr.s
class Reaction:
    """Class for reactions"""
    mid = attr.ib()
    reaction = attr.ib()
    uid = attr.ib()
    thread = attr.ib()
    raw = attr.ib()
    bot = attr.ib()
