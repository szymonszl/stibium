"""This module provides the classes for creating event handlers"""

import re
from .dataclasses import Message

class BaseHandler:
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

class CommandHandler(BaseHandler):
    """
    Event handler for command messages

    Handlers created from this class react to commands, commands being messages
    starting with a command prefix (defined during bot instantiation) with
    a name and possibly arguments.
    Example commands:
    !echo test (the prefix is "!", command is "echo", args is "test")
    :help (prefix is ":", command is "help, args is "")
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
        args = match.group("args")
        event_data.args = args
        if self.wait:
            bot_object.reply(event_data, 'Please wait...')
        self.handlerfn(event_data, bot_object)
