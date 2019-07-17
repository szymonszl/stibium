"""This module provides internationalization"""
import gettext
import os
import locale

from ._logs import log

localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locales')
tr = gettext.translation('carbonium', localedir=localedir, fallback=True)
tr.install()
_ = tr.gettext
