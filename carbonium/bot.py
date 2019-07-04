import types
import json

import fbchat
from fbchat import models

from ._logs import log

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
        log.info('Logged in!')

    def listen(self):
        log.info('Starting listening...')
        self.fbchat_client.listen()

