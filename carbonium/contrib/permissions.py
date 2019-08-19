"""This module provides the Permissions contrib class"""

import types
import json

from ..handlers import CommandHandler
from ..dataclasses import Thread
from .._i18n import _

class Permissions(object):
    """
    This class provides a system for disabling access to commands.

    The user set as admin (can be passed an uid or a Thread) will
    have access to a management command (manage_cmd, default 'manage')
    and can add users to groups. Users added to such group, will not
    have access to commands wrapped by the `block` method.
    Groups and users are stored in json format, in a file
    which path is in `db_file`.
    """
    _db = {}
    _admin = None
    _db_file = None
    _manage_cmd = None
    def __init__(self, db_file, admin, manage_cmd='manage'):
        self._admin = Thread.from_user_uid(admin).id_
        self._db_file = db_file
        self._manage_cmd = manage_cmd
        self._load()

    def _load(self):
        with open(self._db_file) as fd:
            self._db = json.load(fd)

    def _save(self):
        with open(self._db_file, 'w') as fd:
            json.dump(self._db, fd)

    def block(self, group, handler=None, notify=True): #AAAA
        """
        Block members of `group` from using a command.
        Can be used as a decorator, if handler=None.
        If notify is True, user blocked from using a command
        will receive a message telling them they can't use
        the command.
        """
        self._assert_group(group)
        if not notify:
            def wrapper(han):
                oldcheck = han.check
                def hook(self_, event, bot):
                    if event.uid in self._db[group]:
                        return False
                    return oldcheck(event, bot)
                setattr(
                    han,
                    'check',
                    types.MethodType(hook, han)
                )
                return han
        else:
            def wrapper(han):
                oldexec = han.execute
                def hook(self_, event, bot):
                    if event.uid in self._db[group]:
                        event.reply(_("You can't use this command."))
                        return
                    return oldexec(event, bot)
                setattr(
                    han,
                    'execute',
                    types.MethodType(hook, han)
                )
                return han
        if handler:
            return wrapper(handler)
        else:
            return wrapper

    #def allow(self, group, handler=None, notify=True): # TODO

    def _assert_group(self, group):
        if group not in self._db:
            self._db[group] = []
            self._save()

    def _manage(self, message, bot):
        if message.uid != self._admin:
            message.reply(_("You can't use this command."))
            return
        args = message.args.split()
        if len(args) != 3:
            message.reply(
                # TRANSLATORS: "add", "remove", and "reply" are keywords, do not change them
                _('Not enough arguments.\n{prefix}{cmd} [add|ban|remove|unban] <group> [reply|<uid>]')\
                    .format(prefix=bot.prefix, cmd=self._manage_cmd)
            )
            return
        # Get the UID of the targeted person
        if args[2] == 'reply':
            uid = message.replied_to.uid
        else:
            uid = args[2]
        self._assert_group(args[1])
        if args[0] in ('add', 'ban'):
            self._db[args[1]].append(uid)
            message.reply(
                _('Added {uid} to group {group!r}').format(uid=uid, group=args[1])
            )
        elif args[0] in ('remove', 'unban'):
            if uid in self._db[args[1]]:
                self._db[args[1]].remove(uid)
                message.reply(
                   _('Removed {uid} from group {group!r}').format(uid=uid, group=args[1])
                )
            else:
                message.reply(_('User {uid} was not in group.').format(uid=uid))
        else:
            message.reply(_('Unknown subcommand'))
        self._save()

    def handler(self):
        """Returns a handler which needs to be registered"""
        return CommandHandler(self._manage, self._manage_cmd)
