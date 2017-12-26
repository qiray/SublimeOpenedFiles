#!/usr/bin/python
# -*- coding: utf-8 -*-

import sublime

ST3 = int(sublime.version()) >= 3000

if ST3:
    SYNTAX_EXTENSION = '.sublime-syntax'
else:
    SYNTAX_EXTENSION = '.hidden-tmLanguage'

debug_level = 1
untitled_name = 'untitled' #const

def debug(level, *args):
    if level <= debug_level:
        print('[DEBUG]', level, args)
