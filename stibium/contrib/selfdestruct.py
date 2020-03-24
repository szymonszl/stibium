"""This module provides the SelfDestructMessage class"""

from ..handlers import TimeoutHandler
from ..dataclasses import Message

class SelfDestructMessage(TimeoutHandler):
    """
    Self-destructing message handler

    This handler will automatically remove ("unsend")
    a message after a set timeout.
    """
    mid = None
    def __init__(self, mid, timeout):
        super().__init__(handler=None, timeout=timeout)
        self.mid = mid
    async def setup(self, bot):
        if self.mid is None:
            raise Exception(f'MID for {type(self).__name__} not provided')
        if isinstance(self.mid, Message):
            self.mid = self.mid.mid
        else:
            self.mid = str(self.mid)
    async def handlerfn(self, event, bot):
        # TODO make this a bot function, instead of a fbchat one
        await bot.fbchat_client.unsend(mid=self.mid)
