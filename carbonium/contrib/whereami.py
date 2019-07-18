"""This module provides the WhereAmI contrib command"""
from ..handlers import CommandHandler
from ..dataclasses import Message

class WhereAmICommand(CommandHandler):
    """
    "whereami" command

    This command replies to a message with
    the thread it was received from.
    """

    def __init__(self, command='whereami'):
        super().__init__(self._run, command, timeout=None, wait=False)

    def _run(self, message: Message, bot_object):
        message.reply(repr(message.thread))
