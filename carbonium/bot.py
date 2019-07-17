"""This module provies the main Bot class"""

import types
import time
import traceback
import json
import threading
import sched

import fbchat
from fbchat import models

from ._logs import log
from .dataclasses import Thread, Message, Reaction
from .handlers import BaseHandler


class Bot(object):
    """Main Carbonium Bot class"""
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
        self.owner = str(owner).strip()
        log.debug('Object created')

    def login(self):
        """Log in to the bot account"""
        log.debug('login called')
        try:
            with open(self.fb_login[2], 'r') as fd:
                cookies = json.load(fd)
        except OSError:
            cookies = {}
        self.fbchat_client = fbchat.Client(
            self.fb_login[0], self.fb_login[1], session_cookies=cookies, logging_level=30
        )
        with open(self.fb_login[2], 'w') as fd:
            cookies = self.fbchat_client.getSession()
            json.dump(cookies, fd)
        log.debug('Created and logged in the fbchat client, now hooking callbacks...')
        for event in self._handlers.keys():
            self._hook_function(event)
        self._logged_in = True
        log.info('Logged in!')


    def _hook_function(self, hookedfunction):
        log.debug('Hooking function %s', hookedfunction)
        if hookedfunction == '_timeout':
            return
        if hookedfunction in self._hooked_functions:
            return
        def hook(self_, **kwargs): # pylint: disable=unused-argument
            self._fbchat_callback_handler(hookedfunction, kwargs)
            log.debug('Function %s called', hookedfunction)
        setattr(
            self.fbchat_client,
            hookedfunction,
            types.MethodType(hook, self.fbchat_client)
        )

    def _timeout_daemon(self):
        log.debug('Started timeout daemon')
        while True:
            # the thread is a daemon, so this while does not need to be exited
            self._scheduler.run()
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
        self.fbchat_client.listen()

    def register(self, *handlers: BaseHandler):
        """Register handlers"""
        for handler in handlers:
            log.debug('Registering a handler for function %s', repr(handler))
            if handler.event is None:
                raise Exception('Handler did not define event type')
            if handler.event not in self._handlers.keys():
                self._handlers[handler.event] = []
                if self._logged_in:
                    self._hook_function(handler.event)
            handler.setup(self)
            self._handlers[handler.event].append(handler)
            if handler.timeout is not None:
                self._scheduler.enter(
                    handler.timeout,
                    0,
                    self._handle_timeout,
                    argument=(handler,)
                )

    def _handle_timeout(self, handler: BaseHandler):
        self._run_untrusted(
            handler.on_timeout,
            args=(self,),
            thread=None,
            notify=False
        )
        self._handlers[handler.event].remove(handler)

    def send(self, text, thread, mentions=None, reply=None):
        """Send a message to a specified thread"""
        # TODO: more settings (in kwargs), like attachments
        if thread is None:
            raise Exception('Could not send message: `thread` is None')
        message = None
        if isinstance(mentions, list):
            message = models.Message.formatMentions(text, *mentions)
        if message is None:
            message = models.Message(text=text)
        if reply is not None:
            message.reply_to_id = reply
        log.info('Sending a message to thread %s', repr(thread))
        return self.fbchat_client.send(
            message,
            thread_id=thread.id_,
            thread_type=thread.type_
        )

    def get_user_name(self, uid):
        """Get the name of the user specified by uid"""
        uid = str(uid)
        name = self._username_cache.get(uid)
        if name is None:
            name = self.fbchat_client.fetchUserInfo(uid)[uid].name
            self._username_cache[uid] = name
        return name

    def _fbchat_callback_handler(self, event, kwargs): # kwargs are passed straight as a dict, no **
        thread = Thread.fromkwargs(kwargs)
        if event == 'onMessage': # TODO: move to dict?
            self.fbchat_client.markAsDelivered(thread.id_, kwargs['mid'])
            processed = Message.fromkwargs(kwargs, self)
        elif event == 'onReactionAdded':
            processed = Reaction.fromkwargs(kwargs, self)
        else:
            processed = kwargs
        for handler in self._handlers.get(event, []):
            valid = self._run_untrusted(
                handler.check,
                args=[processed, self],
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
                    thread=Thread(id_=self.owner)
                )
            elif valid:
                log.debug('Executing %s, reacting to %s', handler, event)
                self.fbchat_client.markAsRead(thread.id_)
                self.fbchat_client.setTypingStatus(
                    models.TypingStatus.TYPING,
                    thread_type=thread.type_,
                    thread_id=thread.id_,
                )
                time.sleep(0.3) # for safety from bot detection
                self._run_untrusted(
                    handler.execute,
                    args=[processed, self],
                    thread=thread,
                    catch_keyboard=True
                )
                self.fbchat_client.setTypingStatus(
                    models.TypingStatus.STOPPED,
                    thread_type=thread.type_,
                    thread_id=thread.id_,
                )

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
                short_error_message = '\n'.join([
                    'An unexpected error occured, and the action could not be completed.',
                    'The administrator has been notified.',
                    'Error:',
                    trace.splitlines()[-1],
                ])
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
            self.send(error_message, Thread(id_=self.owner))
            return default
        except KeyboardInterrupt as ex:
            if catch_keyboard:
                if thread is not None and notify:
                    self.send('The command has been interrupted by admin', thread)
                return default
            raise ex
