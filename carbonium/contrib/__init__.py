"""
This module contains common example handlers.
They can be used in bots or be referenced as
examples of handlers.
"""
from .echo import EchoCommand
from .info import InfoCommand
from .pins import Pins
from .whereami import WhereAmICommand
from .forward import Forward
from .selfdestruct import SelfDestructMessage

__all__ = [
    'EchoCommand',
    'InfoCommand',
    'Pins',
    'WhereAmICommand',
    'Forward',
    'SelfDestructMessage',
]