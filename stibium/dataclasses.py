"""This module provides the data classes for Stibium"""
import attr
from fbchat import ThreadType, MessageReaction

@attr.s
class Thread(object):
    """Class for containing thread's type and id"""
    id_ = attr.ib(converter=str)
    type_ = attr.ib(default=ThreadType.USER)
    @classmethod
    async def fromkwargs(cls, kwargs): # kwargs are passed as dict
        """Create a Thread class from a handler's kwargs"""
        id_ = kwargs.get('thread_id')
        if id_ is None:
            return
        return cls(
            id_=id_,
            type_=kwargs.get('thread_type', ThreadType.USER),
        )

    @classmethod
    def from_user_uid(cls, uid):
        """
        Returns an USER Thread class, either from the argument
        or created from the passed UID.
        Can be passed either a ready Thread class or an UID.
        """
        if isinstance(uid, cls):
            return uid
        else:
            return cls(id_=uid, type_=ThreadType.USER)

    @classmethod
    def from_group_uid(cls, uid):
        """
        Returns a GROUP Thread class, either from the argument
        or created from the passed UID.
        Can be passed either a ready Thread class or an UID.
        """
        if isinstance(uid, cls):
            return uid
        else:
            return cls(id_=uid, type_=ThreadType.GROUP)

@attr.s
class Message(object):
    """Class for received messages"""
    mid = attr.ib()
    text = attr.ib()
    args = attr.ib(init=False)
    uid = attr.ib()
    thread = attr.ib()
    replied_to = attr.ib()
    timestamp = attr.ib()
    created_at = attr.ib()
    reactions = attr.ib()
    raw = attr.ib(repr=False)
    bot = attr.ib()

    async def reply(self, text, **kwargs):
        """Send a message to a conversation that the message was received from"""
        if kwargs.get('reply', False): # if reply=True
            kwargs['reply'] = self.mid
        return await self.bot.send(text, self.thread, **kwargs)

    async def get_author_name(self):
        """Get message author's name"""
        return await self.bot.get_user_name(self.uid)

    @classmethod
    async def fromkwargs(cls, kwargs, bot):
        """Create a Message class from a handler's kwargs"""
        return await cls.from_model(
            model=kwargs['message_object'],
            thread=await Thread.fromkwargs(kwargs),
            bot=bot,
            raw=kwargs
        )

    @classmethod
    async def from_model(cls, model, thread, bot, raw=None):
        """Create a Message class from fbchat.Message"""
        if model is None:
            return None
        return cls(
            text=model.text,
            uid=model.author,
            mid=model.uid,
            thread=thread,
            replied_to=await cls.from_model(model.replied_to, thread, bot),
            timestamp=model.created_at.timestamp(),
            created_at=model.created_at,
            reactions=model.reactions,
            raw=raw,
            bot=bot,
        )

    @classmethod
    async def from_mid(cls, mid, thread, bot):
        """Create a Message class from a message ID"""
        model = await bot.fbchat_client.fetch_message_info(mid, thread.id_)
        return await cls.from_model(
            model,
            thread,
            bot
        )

@attr.s
class Reaction(object):
    """Class for reactions"""
    mid = attr.ib()
    reaction = attr.ib()
    uid = attr.ib()
    thread = attr.ib()
    message = attr.ib()
    raw = attr.ib(repr=False)
    bot = attr.ib()

    @classmethod
    async def fromkwargs(cls, kwargs, bot):
        """Create a Reaction class from a handler's kwargs"""
        thread = await Thread.fromkwargs(kwargs)
        mid = kwargs['mid']
        message = await Message.from_mid(mid, thread, bot)
        return cls(
            mid=mid,
            reaction=kwargs['reaction'],
            uid=kwargs['author_id'],
            thread=thread,
            message=message,
            raw=kwargs,
            bot=bot,
        )
