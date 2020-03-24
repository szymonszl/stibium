"""This class provides the hooks to the standard fbchat Client class"""
import fbchat
from .dataclasses import Thread, Message, Reaction


class Client(fbchat.Client):
    pass # FIXME