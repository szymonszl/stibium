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
        text = _('"{quote}" - {author}')\
            .format(quote=message.args, author=message.get_author_name())
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
            return _('running Carbonium v{version}').format(version=__version__)
        if x == 'prefix':
            return _('Prefix: {prefix}').format(prefix=repr(bot.prefix))
        if x == 'user':
            uid = bot.fbchat_client.uid
            username = bot.get_user_name(uid)
            return _('Logged in as {username} ({uid})').format(username=username, uid=uid)
        if x == 'hostname':
            return _('Server: {hostname}').format(hostname=os.uname()[1])
        if x == 'pid':
            return _('PID: {pid}').format(pid=os.getpid())
        if x == 'uptime':
            return _('Uptime: {uptime}').format(uptime='TODO') # TODO uptime

    def _run(self, message: Message, bot_object):
        response = []
        for k, v in self.options.items():
            if v:
                response.append(self._get_data(k, bot_object))
        message.reply('\n'.join(response))
