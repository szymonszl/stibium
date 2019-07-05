"""This module provides the data classes for Carbonium"""

import attr

@attr.s
class Message():
    """Class for received messages"""
    mid = attr.ib()
    text = attr.ib()
    args = attr.ib(init=False)
    uid = attr.ib()
    thread_id = attr.ib()
    thread_type = attr.ib()
    raw = attr.ib()
