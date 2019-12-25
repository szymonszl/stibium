"""This module provies the main Bot class"""

import time
import traceback
import json
import asyncio
import pickle

import fbchat

from ._fbclient import Client
from ._logs import log
from .dataclasses import Thread
from .handlers import BaseHandler
from ._i18n import _


class Bot(object):
    """Main Stibium Bot class"""
    loop = None
    name = None
    owner = None
    fb_login = ()
    fbchat_client = None
    command_prefix = None
    _logged_in = False
    _handlers = {}
    _hooked_functions = []
    _username_cache = {}

    def __init__(self, loop, name, prefix, fb_login, owner):
        log.debug('__init__ called')
        self.loop = loop
        self.name = name
        self.prefix = prefix
        self.fb_login = fb_login
        if owner:
            self.owner = Thread.from_user_uid(owner)
        else:
            log.warning('Owner not set, DM error reporting disabled!')
        log.debug('Object created')

    async def login(self):
        """Log in to the bot account"""
        log.debug('login called')
        try:
            with open(self.fb_login[2], 'rb') as fd:
                cookies = pickle.load(fd)
        except OSError:
            cookies = {}
        self.fbchat_client = Client(loop=self.loop)
        await self.fbchat_client.start(
            self.fb_login[0], self.fb_login[1], session_cookies=cookies
        )
        self.fbchat_client.stibium_callback = self._fbchat_callback_handler
        self.fbchat_client.stibium_obj = self
        with open(self.fb_login[2], 'wb') as fd:
            cookies = self.fbchat_client.get_session()
            pickle.dump(cookies, fd)
        log.debug('Created and logged in the fbchat client, now hooking callbacks...')
        self._logged_in = True
        log.info('Logged in!')

    def listen(self):
        """Start listening for events"""
        if not self._logged_in:
            raise Exception('The bot is not logged in yet')
        log.info('Starting listening...')
        self.fbchat_client.listen()

    def register(self, *handlers: BaseHandler):
        """Register handlers"""
        for handler in handlers:
            log.debug('Registering a handler for function %s', repr(handler))
            if handler.event is None:
                raise Exception('Handler did not define event type')
            if handler.event == '_recurrent':
                asyncio.create_task(self._handle_recurrent(handler))
                return
            if handler.event == '_timeout':
                asyncio.create_task(self._handle_timeout_handler(handler))
                return
            if handler.event not in self._handlers.keys():
                self._handlers[handler.event] = []
            asyncio.create_task(handler.setup(self))
            self._handlers[handler.event].append(handler)
            if handler.timeout is not None:
                asyncio.create_task(self._handle_timeout(handler))
        if handlers:
            return handlers[0] # for use as a decorator


    async def _handle_timeout(self, handler: BaseHandler):
        await asyncio.sleep(handler.timeout)
        log.debug('Timing out handler %s', handler)
        self._handlers[handler.event].remove(handler)

    async def _handle_timeout_handler(self, handler: BaseHandler):
        await asyncio.sleep(handler.timeout)
        log.debug('Executing handler %s after timeout', handler)
        await self._run_untrusted(
            handler.execute,
            args=(time.time(), self),
            thread=None,
            notify=False
        )

    async def _handle_recurrent(self, handler: BaseHandler):
        while True:
            delay = await self._run_untrusted(
                handler.next_time,
                args=(time.time(),),
                notify=False
            )
            await asyncio.sleep(time.time() - delay)
            log.debug('Executing recurring handler %s', handler)
            await self._run_untrusted(
                handler.execute,
                args=(time.time(), self),
                thread=None,
                notify=False
            )

    async def send(self, text, thread, mentions=None, reply=None):
        """Send a message to a specified thread"""
        # TODO: add attachments, both here and in onMessage
        if thread is None:
            raise Exception('Could not send message: `thread` is None')
        message = None
        if mentions is not None:
            message = fbchat.Message.format_mentions(text, *mentions)
        if message is None:
            message = fbchat.Message(text=text)
        if reply is not None:
            message.reply_to_id = reply
        log.info('Sending a message to thread %s', repr(thread))
        return await self.fbchat_client.send(
            message,
            thread_id=thread.id_,
            thread_type=thread.type_
        )

    async def get_user_name(self, uid):
        """Get the name of the user specified by uid"""
        uid = str(uid)
        name = self._username_cache.get(uid)
        if name is None:
            userinfo = await self.fbchat_client.fetch_user_info(uid)
            name = userinfo[uid].name
            self._username_cache[uid] = name
        return name

    async def _fbchat_callback_handler(self, func, thread, event):
        for handler in self._handlers.get(func, []):
            valid = await self._run_untrusted(
                handler.check,
                args=[event, self],
                default='error',
                thread=thread,
                notify=False
            )
            if valid == 'error':
                self._handlers.get(func, []).remove(handler)
                errormsg = f'The handler {handler} was disabled, because of causing an exception.'
                log.error(errormsg)
                await self.send(
                    errormsg,
                    thread=self.owner
                )
            elif valid:
                log.debug('Executing %s, reacting to %s', handler, event)
                await self.fbchat_client.mark_as_read(thread.id_)
                await self.fbchat_client.set_typing_status(
                    fbchat.TypingStatus.TYPING,
                    thread_type=thread.type_,
                    thread_id=thread.id_,
                )
                await asyncio.sleep(0.3) # for safety from bot detection
                await self._run_untrusted(
                    handler.execute,
                    args=[event, self],
                    thread=thread,
                    catch_keyboard=True
                )
                await self.fbchat_client.set_typing_status(
                    fbchat.TypingStatus.STOPPED,
                    thread_type=thread.type_,
                    thread_id=thread.id_,
                )

    async def _run_untrusted(
            self,
            fun,
            args=None,
            kwargs=None,
            thread=None,
            notify=True,
            default=None,
            catch_keyboard=False
        ):
        try:
            args = args or []
            kwargs = kwargs or {}
            return await asyncio.wait_for(fun(*args, **kwargs), timeout=30)
        except asyncio.TimeoutError:
            if thread is not None and notify:
                await self.send(_('The command took to long to execute and was cancelled.'), thread)
            return default
        except Exception:
            trace = traceback.format_exc()
            if thread is not None and notify:
                short_error_message = \
                    _("An error occured and the action could not be completed.\n"
                      "The administrator has been notified.\n") \
                    + trace.splitlines()[-1]
                await self.send(short_error_message, thread) # notify the end user
            error_message = '\n'.join([
                f'Error while running function {fun.__name__}',
                f'with *args={args}',
                f'**kwargs={kwargs}',
                f'in thread {thread}',
                f'Full traceback:',
                trace,
            ])
            log.error(error_message)
            if self.owner:
                await self.send(error_message, self.owner)
            return default
        except KeyboardInterrupt:
            if catch_keyboard:
                if thread is not None and notify:
                    await self.send(_('The command has been interrupted by admin'), thread)
                return default
            raise
