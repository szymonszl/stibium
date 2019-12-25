"""This module provides the classes for creating event handlers"""

import re
from .dataclasses import Message, Reaction
from ._i18n import _

#pylint: disable=missing-docstring

#### Base handler

class BaseHandler(object):
    """Base class for creating event handlers"""
    event = None
    timeout = None
    handlerfn = None
    def __init__(self, handler=None, timeout=None):
        self.timeout = timeout
        # Note: self.handlerfn is supposed to be
        # defined in custom subclass-based commands,
        # "None" should be then passed to this __init__.
        if handler is not None:
            self.handlerfn = handler
    async def setup(self, bot):
        pass
    async def check(self, event, bot):
        return False
    async def execute(self, event, bot):
        if callable(self.handlerfn):
            # Note: handler functions should be called
            # with positional parameters, in order to
            # let 'event' be renamed to a more fitting name
            # (like Message for onMessage handlers)
            await self.handlerfn(event, bot)

#### Generic handlers

class CommandHandler(BaseHandler):
    """
    Event handler for command messages

    Handlers created from this class react to commands, commands being messages
    starting with a command prefix (defined during bot instantiation) with
    a name and possibly arguments.
    Example commands:
    !echo test (the prefix is "!", command is "echo", args is "test")
    %help (prefix is "%", command is "help, args is "")
    """
    event = 'message'
    command = None
    prefix = None
    regex = None
    timeout = None
    wait = False
    def __init__(self, handler, command, wait=False, timeout=None):
        super().__init__(handler=handler, timeout=timeout)
        self.command = command
        self.wait = wait
    def __repr__(self):
        return f'<{type(self).__name__} for {repr(self.command)}>'
    async def setup(self, bot):
        self.prefix = bot.prefix
        # regex for: (assumng prefix=%)
        # %command [args] # or
        # % command [args]
        # with command being case-insensitive
        self.regex = re.compile(
            r'^{prefix}\s?{command}($|\s(?P<args>.+))$'.format(
                prefix=self.prefix, command=self.command
            ),
            re.IGNORECASE
        )
    async def check(self, event: Message, bot):
        if event.text is None:
            return False
        match = self.regex.match(event.text)
        if match is None:
            return False
        return True
    async def execute(self, event: Message, bot):
        match = self.regex.match(event.text)
        # parse out args for easier processing
        args = match.group('args') or ''
        event.args = args
        if self.wait:
            await event.reply(_('Please wait...'))
        await super().execute(event, bot)
    @classmethod
    def create(cls, command, timeout=None, wait=False):
        def wrapper(fun):
            return cls(command=command, handler=fun, wait=wait, timeout=timeout)
        return wrapper

class ReactionHandler(BaseHandler):
    """
    Event handler for reactions

    Handlers created from this class react to reactions
    added to a specific message (which can be provided
    as a Message object or directly as a message id)
    """
    event = 'reaction_added'
    mid = None
    def __init__(self, handler, mid, timeout=None):
        super().__init__(handler=handler, timeout=timeout)
        self.mid = mid
    def __repr__(self):
        return f'<{type(self).__name__} mid={repr(self.mid)}>'
    async def setup(self, bot):
        if isinstance(self.mid, Message):
            self.mid = self.mid.mid
        else:
            self.mid = str(self.mid)
    async def check(self, event: Reaction, bot):
        if event.mid == self.mid:
            return True
        return False
    @classmethod
    def create(cls, mid, timeout=None):
        def wrapper(fun):
            return cls(handler=fun, mid=mid, timeout=timeout)
        return wrapper

class TimeoutHandler(BaseHandler):
    """
    Event handler for timeouts

    Handlers created from this class do not react to messages,
    but are started a set amount of time after they are registered.
    """
    event = '_timeout'
    def __init__(self, handler, timeout):
        if timeout is None:
            raise Exception(f'Timeout for {type(self).__name__} not provided')
        super().__init__(handler=handler, timeout=timeout)
    @classmethod
    def create(cls, timeout):
        def wrapper(fun):
            return cls(handler=fun, timeout=timeout)
        return wrapper

class RecurrentHandler(BaseHandler):
    """
    A recurring event handler

    This handler will execute the provided function
    regulary on a specified schedule.

    The schedule is defined by the `next_time` method,
    which is called with the current time as
    a unix timestamp (float) and should return
    the unix timestamp of the next execution
    """
    event = '_recurrent'
    def __init__(self, handler, nexthandler):
        super().__init__(handler=handler, timeout=None)
        if nexthandler is not None:
            self.nextfn = nexthandler # supposed to be replaced when custom subclassing
    async def next_time(self, now):
        if callable(self.nextfn):
            return await self.nextfn(now)
    @classmethod
    def create(cls, nexthandler):
        def wrapper(fun):
            return cls(handler=fun, nexthandler=nexthandler)
        return wrapper
