"""This module provides the Permissions contrib class"""

import types
import json
import time
import datetime

from ..handlers import CommandHandler
from ..dataclasses import Message, Thread
from .._i18n import _

class Permissions(object):
    """
    This class provides a system for disabling access to commands.

    -- TODO --

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
                _('Not enough arguments.\n{prefix}{cmd} [add|remove] <group> [reply|<uid>]')
            )
            return
        # Get the UID of the targeted person
        if args[2] == 'reply':
            uid = message.replied_to.uid
        else:
            uid = args[2]
        self._assert_group(args[1])
        if args[0] == 'add':
            self._db[args[1]].append(uid)
            message.reply(
                _('Added {uid} to group {group!r}').format(uid=uid, group=args[1])
            )
        elif args[0] == 'remove':
            if uid in self._db[args[1]]:
                self._db[args[1]].remove(uid)
            else:
                message.reply(_('User {uid} was not in group.'))
        self._save()

    def handler(self):
        """Returns a handler which needs to be registered"""
        return CommandHandler(self._manage, self._manage_cmd)
