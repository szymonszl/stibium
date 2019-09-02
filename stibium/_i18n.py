"""This module provides internationalization"""
import gettext
import os

localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locales')
tr = gettext.translation('stibium', localedir=localedir, fallback=True)
tr.install()
_ = tr.gettext
