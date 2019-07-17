from ..handlers import CommandHandler
from ..dataclasses import Message

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
