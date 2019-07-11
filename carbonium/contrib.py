"""
This module contains common example handlers.
They can be used in bots or be referenced as
examples of handlers.
"""
import os

from .handlers import CommandHandler
from .dataclasses import Message
from . import __version__

# Example of a very simple command
class EchoCommand(CommandHandler):
    """
    Echo command

    This command replies to a message with its contents.
    """

    def __init__(self, command='echo'):
        super().__init__(self._run, command, timeout=None, wait=False)

    # Try not to override the execute method of CommandHandler,
    # since it provides useful preprocessing.
    # Instead create a method and pass it to super().__init__
    def _run(self, message: Message, bot_object):
        text = f'"{message.args}" - {message.get_author_name()}'
        message.reply(text)

# Example of a more sophisticated command
class InfoCommand(CommandHandler):
    """
    Bot information command

    This handler creates a command responding with information
    about the bot. The command is by default called 'info',
    but this can be changed with the `command` kwarg.
    Sent information can be customized by the `options` kwarg.
    Available options:
    name carbonium prefix user hostname pid uptime
    """
    options = {
        'name': True,
        'carbonium': True,
        'prefix': True,
        'user': True,
        'hostname': False,
        'pid': False,
        'uptime': True,
    }

    def __init__(self, command='info', options=None):
        super().__init__(self._run, command, timeout=None, wait=False)
        if isinstance(options, dict):
            for k, v in options.items():
                if k in self.options:
                    self.options[k] = v

    def _get_data(self, x, bot):
        if x == 'name':
            return bot.name
        if x == 'carbonium':
            return f'running Carbonium v{__version__}'
        if x == 'prefix':
            return f'Prefix: {bot.prefix!r}'
        if x == 'user':
            uid = bot.fbchat_client.uid
            user_name = bot.get_user_name(uid)
            return f'Logged in as {user_name} ({uid})'
        if x == 'hostname':
            return f'Server: {os.uname()[1]}'
        if x == 'pid':
            return f'PID: {os.getpid()}'
        if x == 'uptime':
            return 'Uptime: TODO' # TODO

    def _run(self, message: Message, bot_object):
        response = []
        for k, v in self.options.items():
            if v:
                response.append(self._get_data(k, bot_object))
        message.reply('\n'.join(response))
