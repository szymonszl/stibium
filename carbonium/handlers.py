"""This module provides the classes for creating event handlers"""

import re
from .dataclasses import Message, Reaction
from ._i18n import _

# TODO: "deprecate" creating handlers directly from __init__
#       (to ease subclassing, see `contrib/echo.py:15`)
#       instead opt for @classmethods (preferably also
#       creating one for decorating)

#### Base handler

class BaseHandler(object):
    """Base class for creating event handlers"""
    handlerfn = None
    event = None
    timeout = None
    def __init__(self):
        if self.event is None:
            raise Exception('No hook type was defined, was the class subclassed correctly?')
    def check(self, event_data, bot_object): # pylint: disable=unused-argument
        return False
    def execute(self, event_data, bot_object):
        if callable(self.handlerfn):
            self.handlerfn(event_data, bot_object) # pylint: disable=not-callable
    def setup(self, bot_object): # pylint: disable=unused-argument
        pass
    def on_timeout(self, bot_object): # pylint: disable=unused-argument
        pass

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
    event = 'onMessage'
    command = None
    prefix = None
    regex = None
    def __init__(self, fn, command, timeout=None, wait=False):
        super().__init__()
        self.handlerfn = fn
        self.command = command
        self.timeout = timeout
        self.wait = wait

    @classmethod
    def register(cls, bot, command, timeout=None, wait=False):
        """A decorator to create and register commands. Reaturns a CommandHandler."""
        def register_decorator(fn):
            cmd = cls(fn, command, timeout, wait)
            bot.register(cmd)
            return cmd
        return register_decorator

    def __repr__(self):
        return f'<{type(self).__name__} for {repr(self.command)}>'

    def setup(self, bot_object):
        self.prefix = bot_object.prefix
        self.regex = re.compile(
            r'^{prefix}\s?{command}($|\s(?P<args>.+))$'.format(
                prefix=self.prefix, command=self.command
            ),
            re.IGNORECASE
        )
    def check(self, event_data: Message, bot_object):
        if event_data.text is None:
            return False
        match = self.regex.match(event_data.text)
        if match is None:
            return False
        return True

    def execute(self, event_data: Message, bot_object):
        match = self.regex.match(event_data.text)
        args = match.group('args') or ''
        event_data.args = args
        if self.wait:
            event_data.reply(_('Please wait...'))
        self.handlerfn(event_data, bot_object)

class ReactionHandler(BaseHandler):
    """
    Event handler for reactions

    Handlers created from this class react to reactions
    added to a specific message (which can be provided
    as a Message object or directly as a message id)
    """
    event = 'onReactionAdded'
    mid = None
    def __init__(self, fn, mid, timeout=None):
        super().__init__()
        self.handlerfn = fn
        if isinstance(mid, Message):
            self.mid = mid.mid
        else:
            self.mid = str(mid)
        self.timeout = timeout
    def check(self, event_data: Reaction, bot_object):
        if event_data.mid == self.mid:
            return True
        return False

class TimeoutHandler(BaseHandler):
    """
    Event handler for timeouts

    Handlers created from this class do not react to messages,
    but are started a set amount of time after they are registered.
    """
    event = '_timeout'
    def __init__(self, fn, timeout):
        super().__init__()
        self.handlerfn = fn
        self.timeout = timeout
    def execute(self, event_data, bot_object): # TODO: remove this shitty hack
        pass
    def on_timeout(self, bot_object):
        if callable(self.handlerfn):
            self.handlerfn(bot_object)

class SelfDestructMessage(TimeoutHandler):
    """
    Self-destructing message handler


    This handler will automatically remove ("unsend")
    a message after a set timeout.
    """
    def __init__(self, mid, timeout):
        super().__init__(self._run, timeout)
        if isinstance(mid, Message):
            self.mid = mid.mid
        else:
            self.mid = str(mid)

    def _run(self, bot_object):
        bot_object.fbchat_client.unsend(mid=self.mid)

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
    def __init__(self, fn, next_time):
        super().__init__()
        self.handlerfn = fn
        self.nextfn = next_time
    def execute(self, event_data, bot_object):
        if callable(self.handlerfn):
            self.handlerfn(bot_object)
    def next_time(self, now):
        if callable(self.nextfn):
            return self.nextfn(now)
