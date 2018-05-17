#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file uses functions from Sublime FileBrowser plugin with MIT license - https://packagecontrol.io/packages/FileBrowser

import os
from os.path import basename
import sublime

ST3 = int(sublime.version()) >= 3000

if ST3:
    from .common import SYNTAX_EXTENSION
else:  # ST2 imports
    from common import SYNTAX_EXTENSION

def first(seq, pred):
    '''similar to built-in any() but return the object instead of boolean'''
    return next((item for item in seq if pred(item)), None)

def set_proper_scheme(view):
    '''set color scheme'''
    settings = sublime.load_settings('opened_files.sublime-settings')
    if view.settings().get('color_scheme') == settings.get('color_scheme'):
        return
    view.settings().set('color_scheme', settings.get('color_scheme'))

def get_group(groups, nag):
    '''
    groups  amount of groups in window
    nag     number of active group
    return number of neighbour group
    '''
    if groups <= 4 and nag < 2:
        group = 1 if nag == 0 else 0
    elif groups == 4 and nag >= 2:
        group = 3 if nag == 2 else 2
    else:
        group = nag - 1
    return group

def set_active_group(window, view, other_group, view_exist):
    """Function from SublimeFileBrowser with some modifications"""
    nag = window.active_group()
    if other_group:
        group = 0 if other_group == 'left' else 1
        groups = window.num_groups()
        if groups == 1:
            width = 0.2 #default value
            cols = [0.0, width, 1.0] if other_group == 'left' else [0.0, 1 - width, 1.0]
            window.set_layout({"cols": cols, "rows": [0.0, 1.0], "cells": [[0, 0, 1, 1], [1, 0, 2, 1]]})
        elif view:
            group = get_group(groups, nag)
        if not view_exist:
            window.set_view_index(view, group, 0)
    else:
        group = nag

    # when other_group is left, we need move all views to right except our view
    if nag == 0 and other_group == 'left' and group == 0:
        for v in reversed(window.views_in_group(nag)[1:]):
            window.set_view_index(v, 1, 0)


def set_view(view_id, window):
    """select or create view for plugin"""
    view = None
    if view_id:
        view = first(window.views(), lambda v: v.id() == view_id)

    if not view:
        view = window.new_file()
        view.settings().add_on_change('color_scheme', lambda: set_proper_scheme(view))
        view.set_syntax_file('Packages/OpenedFiles/opened_files' + SYNTAX_EXTENSION)
        view.set_scratch(True)

    return view


def show(window, path, view_id=None, ignore_existing=False, single_pane=False, other_group=False, focus=False):
    """
    Determines the correct view to use, creating one if necessary, and prepares it.
    """
    view_exist = first(window.views(), lambda v: v.settings().get("opened_files_type"))

    if other_group:
        prev_focus = window.active_view()
        # simulate 'toggle sidebar':
        if prev_focus and 'opened_files' in prev_focus.scope_name(0):
            return prev_focus #don't close the view - we can use it again

    if not path.endswith(os.sep):
        path += os.sep

    view = set_view(view_id, window)

    set_active_group(window, view, other_group, view_exist)

    if other_group and prev_focus:
        window.focus_view(prev_focus)

    if path == os.sep:
        view_name = os.sep
    else:
        view_name = basename(path.rstrip(os.sep))

    if ST3:
        name = u"𝌆 {0}".format(view_name)
    else:
        name = u"■ {0}".format(view_name)

    view.set_name(name)
    view.settings().set('opened_files_type', True)

    # forcibly shoot on_activated, because when view was created it didnot have any settings
    window.show_quick_panel(['a', 'b'], None)
    window.run_command('hide_overlay')
    if view_id is None or focus:
        window.focus_view(view)
    return view
