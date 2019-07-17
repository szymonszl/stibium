"""This module provides internationalization"""
import gettext
import os
import locale

from ._logs import log

def _setuplocale(lang):
    if lang is None:
        lang, encoding = locale.getdefaultlocale()
    localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locales')
    tr = gettext.translation('carbonium', localedir=localedir, languages=[lang])
    tr.install()
    log.info('Setting up language %s', lang)
