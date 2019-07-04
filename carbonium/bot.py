import types
import json

import fbchat
from fbchat import models
import attr

from ._logs import log

@attr.s
class Message():
    mid = attr.ib()
    text = attr.ib()
    args = attr.ib()
    uid = attr.ib()
    thread_id = attr.ib()
    thread_type = attr.ib()



class Bot:
    name = None
    owner = None
    fb_login = ()
    fbchat_client = None
    command_prefix = None
    def __init__(self, name, prefix, fb_login, owner):
        log.debug('__init__ called')
        self.name = name
        self.prefix = prefix
        self.fb_login = fb_login
        self.owner = owner
        log.info('Object created')

    def login(self):
        log.debug('login called')
        try:
            with open(self.fb_login[2], 'r') as fd:
                cookies = json.load(fd)
        except OSError:
            cookies = {}
        self.fbchat_client = fbchat.Client(
            self.fb_login[0], self.fb_login[1], session_cookies=cookies
        )
        cookies = self.fbchat_client.getSession()
        json.dump(cookies, open(self.fb_login[2], 'w'))
        log.debug('Created and logged in the fbchat client, now hooking callbacks...')
        hookedfunction = 'onMessage' # for TODO: extend to other callbacks
        def hook(self_, **kwargs):
            self._fbchat_callback_handler(hookedfunction, kwargs)
            log.debug(f'{hookedfunction} called')
        setattr(
            self.fbchat_client,
            hookedfunction,
            types.MethodType(hook, self.fbchat_client)
        )
        log.info('Logged in!')

    def listen(self):
        log.info('Starting listening...')
        self.fbchat_client.listen()

    def _fbchat_callback_handler(self, event, kwargs): # kwargs are passed straight as a dict, no **
        log.warning('Got an event!')
        if event == 'onMessage':
            message = Message(
                text=kwargs["message_object"].text,
                args="__TODO__",
                uid=kwargs["author_id"],
                mid=kwargs["mid"],
                thread_type=kwargs["thread_type"],
                thread_id=kwargs["thread_type"]
            )
            print(message)
