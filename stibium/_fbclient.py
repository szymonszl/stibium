"""This class provides the hooks to the standard fbchat Client class"""
import fbchat
from .dataclasses import Thread, Message, Reaction

class Client(fbchat.Client):
    stibium_callback = lambda **a: a
    stibium_obj = None
    async def on_message(self, **kwargs):
        thread = await Thread.fromkwargs(kwargs)
        await self.mark_as_delivered(thread.id_, kwargs['mid'])
        event = await Message.fromkwargs(kwargs, self.stibium_obj)
        await self.stibium_callback(func='message', thread=thread, event=event)
    async def on_reaction_added(self, **kwargs):
        thread = await Thread.fromkwargs(kwargs)
        event = await Reaction.fromkwargs(kwargs, self.stibium_obj)
        await self.stibium_callback(func='reaction_added', thread=thread, event=event)
