#!/usr/bin/python
# -*- coding: utf-8 -*-

import sublime

ST3 = int(sublime.version()) >= 3000

if ST3:
    SYNTAX_EXTENSION = '.sublime-syntax'
else:
    SYNTAX_EXTENSION = '.hidden-tmLanguage'

DEBUG_LEVEL = 1
UNTITLED_NAME = 'untitled' #const

def debug(level, *args):
    """Log debug info according to debug level"""
    if level <= DEBUG_LEVEL:
        print('[DEBUG]', level, args)
