import re
from .dataclasses import *
from fbchat.models import Message as FBMessage # FIXME

class BaseHandler:
    handlerfn = None
    event = None
    timeout = None
    def __init__(self):
        if self.event is None:
            raise Exception('No hook type was defined, was the class subclassed correctly?')
    def check(self, event_data, bot_object):
        pass
    def setup(self, bot_object):
        pass

class CommandHandler(BaseHandler):
    event = 'onMessage'
    command = None
    prefix = None
    regex = None
    def __init__(self, fn, command, timeout=None, wait=False):
        super().__init__()
        self.handlerfn = fn
        self.command = command
        self.timeout = timeout
        self.wait = wait
    def setup(self, bot_object):
        self.prefix = bot_object.prefix
        self.regex = re.compile(
            r'^{prefix}\s?{command}($|\s(?P<args>.+))$'.format(
                prefix=self.prefix, command=self.command
            )
        )
    def check(self, event_data: Message, bot_object):
        if event_data.text is None:
            return
        match = self.regex.match(event_data.text)
        if match is None:
            return
        args = match.group("args")
        event_data.args = args
        # execute the handler fn
        if self.wait:
            #bot_object.reply(event_data, 'Please wait...') #TODO: add .reply
            bot_object.fbchat_client.send(FBMessage(text='Please wait...'),
                hread_id=event_data.thread_id, thread_type=event_data.thread_type)
        self.handlerfn(event_data, bot_object)
