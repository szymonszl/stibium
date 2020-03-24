from ..handlers import CommandHandler
from ..dataclasses import Message
from .._i18n import _

# Example of a very simple command
class EchoCommand(CommandHandler):
    """
    Echo command

    This command replies to a message with its contents.
    """

    def __init__(self, command='echo'):
        super().__init__(handler=None, command=command)

    # If you're subclassing a handler, try not to override
    # execute, override handlerfn instead
    # and pass None to __init__
    # Also, pylint shows method-hidden for the following declaration,
    # it is a false positive (https://github.com/PyCQA/pylint/issues/414)
    async def handlerfn(self, message: Message, bot):
        text = _('"{quote}" - {author}')\
            .format(quote=message.args, author=await message.get_author_name())
        await message.reply(text)
