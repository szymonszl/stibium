"""This module provides the data classes for Carbonium"""

import attr

@attr.s
class Thread:
    """Class for containing thread's type and id"""
    id_= attr.ib()
    type_ = attr.ib()
    @classmethod
    def fromkwargs(self, kwargs): # kwargs are passed as dict
        """Create a Thread class from a handler's kwargs"""
        return Thread(
            id_=str(kwargs.get("thread_id")),
            type_=kwargs.get("thread_type"),
        )

@attr.s
class Message:
    """Class for received messages"""
    mid = attr.ib()
    text = attr.ib()
    args = attr.ib(init=False)
    uid = attr.ib()
    thread = attr.ib()
    raw = attr.ib()
