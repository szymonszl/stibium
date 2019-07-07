"""This module provides the data classes for Carbonium"""

import attr
from fbchat.models import ThreadType, MessageReaction

@attr.s
class Thread(object):
    """Class for containing thread's type and id"""
    id_ = attr.ib()
    type_ = attr.ib(default=ThreadType.USER)
    @classmethod
    def fromkwargs(cls, kwargs): # kwargs are passed as dict
        """Create a Thread class from a handler's kwargs"""
        id_ = kwargs.get('thread_id')
        if id_ is None:
            return
        return cls(
            id_=str(id_),
            type_=kwargs.get('thread_type', ThreadType.USER),
        )

@attr.s
class Message(object):
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
        if kwargs.get('reply', False): # if reply=True
            kwargs['reply'] = self.mid
        return self.bot.send(text, self.thread, **kwargs)

    def get_author_name(self):
        """Get message author's name"""
        return self.bot.get_user_name(self.uid)

@attr.s
class Reaction(object):
    """Class for reactions"""
    mid = attr.ib()
    reaction = attr.ib()
    uid = attr.ib()
    thread = attr.ib()
    raw = attr.ib()
    bot = attr.ib()
