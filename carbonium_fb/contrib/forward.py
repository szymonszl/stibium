"""This class provides the Forward class"""

import attr

from ..handlers import CommandHandler, ReactionHandler
from ..dataclasses import Thread, ThreadType, Message, Reaction, MessageReaction
from .._i18n import _


@attr.s
class Forward(object):
    """
    This class provides a system for forwarding messages to a group.

    A selected account outside of a group can send a message to
    a group, and any of the group users can respond to it.
    The "send to group" command is by default called "send",
    and "send to user" command is by default called "respond".
    They can be changed by send_cmd and respond_cmd kwargs.

    This class provides two commands, so it has to be registered as:
    `bot.register(*forward.handlers())`
    """
    _group_thread = attr.ib(converter=Thread.from_group_uid)
    _user_thread = attr.ib(converter=Thread.from_user_uid)
    _send_cmd = attr.ib(default='send')
    _respond_cmd = attr.ib(default='respond')

    def _send_fn(self, message: Message, bot_object):
        if message.thread != self._user_thread:
            message.reply(_("You can't use this command."))
            return
        if not message.args:
            message.reply(_('Please provide text to be sent.'))
            return
        bot_object.send(
            _("Message from {user}:\n{message}").format(
                user=message.get_author_name(), message=message.args
            ),
            thread=self._group_thread
        )
        message.reply(_('The message was forwarded.'))
    
    def _respond_fn(self, message: Message, bot_object):
        if message.thread != self._group_thread:
            message.reply(_("You can't use this command."))
            return
        if not message.args:
            message.reply(_('Please provide text to be sent.'))
            return
        def _callback(reaction: Reaction, bot_object):
            if reaction.uid == message.uid:
                if reaction.reaction == MessageReaction.YES:
                    bot_object.send(
                        _("Message from {user}:\n{message}").format(
                            user=message.get_author_name(), message=message.args
                        ),
                        thread=self._user_thread
                    )
                    message.reply(_('The message was forwarded.'))
        mid = message.reply(
            _('Are you sure you want to send this to {user}?\n'
              'Please confirm by reacting {reaction}.').format(
                  user=bot_object.get_user_name(self._user_thread.id_),
                  reaction=MessageReaction.YES.value
            ),
            reply=True
        )
        bot_object.register(ReactionHandler(_callback, mid, timeout=120))

    def handlers(self):
        """Returns a list of handlers that need to be registered"""
        handlers = []
        handlers.append(
            CommandHandler(self._send_fn, self._send_cmd)
        )
        handlers.append(
            CommandHandler(self._respond_fn, self._respond_cmd)
        )
        return handlers
