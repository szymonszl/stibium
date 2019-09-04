"""This class provides the hooks to the standard fbchat Client class"""
import fbchat
from .dataclasses import Thread, Message, Reaction

class Client(fbchat.Client):
    stibium_callback = lambda **a: a
    stibium_obj = None
    def onMessage(self, **kwargs):
        thread = Thread.fromkwargs(kwargs)
        self.markAsDelivered(thread.id_, kwargs['mid'])
        event = Message.fromkwargs(kwargs, self.stibium_obj)
        self.stibium_callback(func='onMessage', thread=thread, event=event)
    def onReactionAdded(self, **kwargs):
        thread = Thread.fromkwargs(kwargs)
        event = Reaction.fromkwargs(kwargs, self.stibium_obj)
        self.stibium_callback(func='onReactionAdded', thread=thread, event=event)
