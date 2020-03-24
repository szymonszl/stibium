"""This module provies the main Bot class"""

import time
import traceback
import json
import threading
import sched

from fbchat import models

from ._fbclient import Client
from ._logs import log
from .dataclasses import Thread
from .handlers import BaseHandler
from ._i18n import _


class Bot(object):
    """Main Stibium Bot class"""
    name = None
    owner = None
    fb_login = ()
    fbchat_client = None
    command_prefix = None
    _logged_in = False
    _handlers = {}
    _hooked_functions = []
    _username_cache = {}
    _scheduler = sched.scheduler(time.time, time.sleep)

    def __init__(self, name, prefix, fb_login, owner):
        log.debug('__init__ called')
        self.name = name
        self.prefix = prefix
        self.fb_login = fb_login
        if owner and False:
            self.owner = None # FIXME
        else:
            log.warning('Owner not set, DM error reporting disabled!')
        log.debug('Object created')

    def login(self):
        """Log in to the bot account"""
        log.debug('login called')
        raise NotImplementedError # FIXME
        log.debug('Created and logged in the fbchat client...')
        self._logged_in = True
        log.info('Logged in!')

    def _timeout_daemon(self):
        log.debug('Started timeout daemon')
        while True:
            # the thread is a daemon, so this while does not need to be exited
            self._scheduler.run(blocking=False)
            time.sleep(1) # wait for more events

    def listen(self):
        """Start listening for events"""
        if not self._logged_in:
            raise Exception('The bot is not logged in yet')
        log.debug('Starting the timeout daemon...')
        timeout_daemon = threading.Thread(
            target=self._timeout_daemon,
            name='TimeoutThread',
            daemon=True
        )
        timeout_daemon.start()
        log.info('Starting listening...')
        raise NotImplementedError # FIXME

    def register(self, *handlers: BaseHandler):
        """Register handlers"""
        for handler in handlers:
            log.debug('Registering a handler for function %s', repr(handler))
            if handler.event is None:
                raise Exception('Handler did not define event type')
            if handler.event == '_recurrent':
                self._scheduler.enterabs(
                    self._run_untrusted(
                        handler.next_time,
                        args=(time.time(),),
                        notify=False
                    ),
                    0,
                    self._handle_recurrent,
                    argument=(handler,)
                )
                return
            if handler.event == '_timeout':
                self._scheduler.enter(
                    handler.timeout,
                    0,
                    self._handle_timeout,
                    argument=(handler,)
                )
                return
            if handler.event not in self._handlers.keys():
                self._handlers[handler.event] = []
            handler.setup(self)
            self._handlers[handler.event].append(handler)
            if handler.timeout is not None:
                self._scheduler.enter(
                    handler.timeout,
                    0,
                    self._handlers[handler.event].remove,
                    argument=(handler,)
                )
        if handlers:
            return handlers[0] # for use as a decorator

    def _handle_timeout(self, handler: BaseHandler):
        self._run_untrusted(
            handler.execute,
            args=(time.time(), self),
            thread=None,
            notify=False
        )

    def _handle_recurrent(self, handler: BaseHandler):
        log.debug('Executing recurring handler %s', handler)
        self._run_untrusted(
            handler.execute,
            args=(time.time(), self),
            thread=None,
            notify=False
        )
        self._scheduler.enterabs(
            self._run_untrusted(
                handler.next_time,
                args=(time.time(),),
                notify=False
            ),
            0,
            self._handle_recurrent,
            argument=(handler,)
        )

    def send(self, text, thread, mentions=None, reply=None):
        """Send a message to a specified thread"""
        # TODO: add attachments, both here and in onMessage
        raise NotImplementedError # FIXME

    def get_user_name(self, uid):
        """Get the name of the user specified by uid"""
        uid = str(uid)
        name = self._username_cache.get(uid)
        if name is None:
            raise NotImplementedError # FIXME
            self._username_cache[uid] = name
        return name

    def _fbchat_callback_handler(self, func, thread, event):
        for handler in self._handlers.get(func, []):
            valid = self._run_untrusted(
                handler.check,
                args=[event, self],
                default='error',
                thread=thread,
                notify=False
            )
            if valid == 'error':
                self._handlers.get(event, []).remove(handler)
                errormsg = f'The handler {handler} was disabled, because of causing an exception.'
                log.error(errormsg)
                self.send(
                    errormsg,
                    thread=self.owner
                )
            elif valid:
                log.debug('Executing %s, reacting to %s', handler, event)
                raise NotImplementedError # FIXME

    def _run_untrusted( # pylint: disable=dangerous-default-value
            self,
            fun,
            args=[],
            kwargs={},
            thread=None,
            notify=True,
            default=None,
            catch_keyboard=False
        ):
        try:
            return fun(*args, **kwargs)
        except Exception:
            trace = traceback.format_exc()
            if thread is not None and notify:
                short_error_message = \
                    _("An error occured and the action could not be completed.\n"
                      "The administrator has been notified.\n") \
                    + trace.splitlines()[-1]
                raise NotImplementedError # FIXME
                self.send(short_error_message, thread) # notify the end user
            error_message = '\n'.join([
                f'Error while running function {fun.__name__}',
                f'with *args={args}',
                f'**kwargs={kwargs}',
                f'in thread {thread}',
                f'Full traceback:',
                trace,
            ])
            log.error(error_message)
            if self.owner: # Report error to admin
                raise NotImplementedError # FIXME
            return default
        except KeyboardInterrupt as ex:
            if catch_keyboard:
                if thread is not None and notify:
                    self.send(_('The command has been interrupted by admin'), thread)
                return default
            raise ex
