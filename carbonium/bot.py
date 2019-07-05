import types
import json

import fbchat
from fbchat import models

from ._logs import log
from .dataclasses import *
from .handlers import *


class Bot:
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
    def __init__(self, name, prefix, fb_login, owner):
        log.debug('__init__ called')
        self.name = name
        self.prefix = prefix
        self.fb_login = fb_login
        self.owner = owner
        log.info('Object created')

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
        if hookedfunction in self._hooked_functions:
            return
        def hook(self_, **kwargs):
            self._fbchat_callback_handler(hookedfunction, kwargs)
            log.debug('Function %s called', hookedfunction)
        setattr(
            self.fbchat_client,
            hookedfunction,
            types.MethodType(hook, self.fbchat_client)
        )


    def listen(self):
        """Start listening for events"""
        if not self._logged_in:
            raise Exception('The bot is not logged in yet')
        log.info('Starting listening...')
        self.fbchat_client.listen()

    def register(self, handler: BaseHandler):
        """Register a handler"""
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
            pass # TODO: implement timeouts

    def send(self, text, thread_id, thread_type, **kwargs):
        """Send a message to a specified thread"""
        # TODO: more settings (in kwargs), like mentions, attachments or replies
        self.fbchat_client.send(
            models.Message(text=text),
            thread_id=thread_id,
            thread_type=thread_type
            )

    def reply(self, reply_to: Message, text, **kwargs):
        """Send a message to a conversation that the message was received from"""
        self.send(text, reply_to.thread_id, reply_to.thread_type, **kwargs)

    def get_user_name(self, uid):
        """Get the name of the user specified by uid"""
        uid = str(uid)
        name = self._username_cache.get(uid)
        if name is None:
            name = self.fbchat_client.fetchUserInfo(uid)[uid].name
            self._username_cache[uid] = name
        return name

    def _fbchat_callback_handler(self, event, kwargs): # kwargs are passed straight as a dict, no **
        if event == 'onMessage': # TODO: modularize that
            message = Message(
                text=kwargs['message_object'].text,
                uid=kwargs['author_id'],
                mid=kwargs['mid'],
                thread_type=kwargs['thread_type'],
                thread_id=kwargs['thread_id']
            )
            for handler in self._handlers['onMessage']:
                handler.check(message, self) # TODO: split check and execute, add error handling
