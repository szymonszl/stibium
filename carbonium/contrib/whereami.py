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
        super().__init__(handler=None, command=command)

    def handlerfn(self, message: Message, bot):
        message.reply(repr(message.thread))
