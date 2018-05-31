#!/usr/bin/python
#*- coding: utf-8 -*-
"""
This project uses some code and ideas from Sublime FileBrowser plugin
with MIT license - https://packagecontrol.io/packages/FileBrowser
"""

import sublime
import sublime_plugin

VERSION_MAJOR = 0
VERSION_MINOR = 9
VERSION_PATCH = 7

ST3 = int(sublime.version()) >= 3000

#TODO: add comments

if ST3:
    from .common import UNTITLED_NAME, debug, SYNTAX_EXTENSION
    from .show import show, first
    from .treeview import Tree
    from .GotoWindow import focus_window
else:  # ST2 imports
    from common import UNTITLED_NAME, debug, SYNTAX_EXTENSION
    from show import show, first
    from treeview import Tree
    from GotoWindow import focus_window

def view_name(view):
    """Function to get view name"""
    result = UNTITLED_NAME
    filename = view.file_name()
    name = view.name()
    if filename is not None and filename != '':
        result = filename
    elif name is not None and name != '':
        result = name
    return result

def generate_trees(view_list, localtrees):
    result = []
    count = 1
    for l in view_list:
        if (len(l) == 0):
            continue
        temp_tree = Tree("Window {}\n".format(count))
        for view in l:
            name = view_name(view)
            temp_tree.add_filename(name, view.id(), is_file=False if view.file_name() is None else True)
        nodes = temp_tree.get_nodes()
        for n in nodes:
            old_node = None
            for tree in localtrees:
                old_node = tree.get_node(n)
                if old_node:
                    break
            new_node = temp_tree.get_node(n)
            if old_node:
                new_node.status = old_node.status
                temp_tree.set_node(n, new_node)
        result.append(temp_tree)
        count += 1
    return result

def draw_view(window, edit, view_object, focus=False, other_window=False):
    plugin_settings = sublime.load_settings('opened_files.sublime-settings')
    group_position = plugin_settings.get('group_position')
    if group_position != 'left' and group_position != 'right':
        group_position = 'left'
    view = show(window, 'Opened Files', other_window=other_window, view_id=OpenedFilesCommand.OPENED_FILES_VIEW, other_group=group_position,focus=focus)
    if not view:
        OpenedFilesCommand.OPENED_FILES_VIEW = None
        return
    OpenedFilesCommand.OPENED_FILES_VIEW = view.id()
    view.set_read_only(False) #Enable edit for pasting result
    view.erase(edit, sublime.Region(0, view.size())) #clear view content
    if isinstance(view_object, list):
        result = ''
        for elm in view_object:
            result += str(elm)
        view.insert(edit, 0, result)
    else:
        view.insert(edit, 0, str(view_object)) #paste result
    view.set_read_only(True) #Disable edit

class OpenedFilesCommand(sublime_plugin.TextCommand): #view.run_command('opened_files')

    OPENED_FILES_VIEW = None
    trees = []

    def run(self, edit, focus=False, other_window=False):
        window = self.view.window()
        #if we already have OpenedFiles window we shouldn't create anymore
        if OpenedFilesListener.current_window is not None and \
            OpenedFilesListener.current_window != window:
            return
        windows = sublime.windows()
        view_list = []
        count = 0
        for win in windows:
            view_list.append([])
            for view in win.views():
                settings = view.settings()
                if settings.get("opened_files_type"):
                    OpenedFilesCommand.OPENED_FILES_VIEW = view.id()
                elif settings.get('dired_path'):
                    pass
                else:
                    view_list[count].append(view)
            count += 1
        OpenedFilesCommand.trees = generate_trees(view_list, OpenedFilesCommand.trees)
        draw_view(window, edit, OpenedFilesCommand.trees, focus, other_window)

class OpenedFilesActCommand(sublime_plugin.TextCommand):
    def run(self, edit, act='default'):
        selection = self.view.sel()[0]
        self.open_file(edit, selection, act)

    def open_file(self, edit, selection, act):
        window = self.view.window()
        (row, _) = self.view.rowcol(selection.begin())
        curtree = 0
        length, prevlength = 0, 0
        for tree in OpenedFilesCommand.trees: #calc used tree
            if length > row:
                break
            prevlength = length
            length += tree.size
            curtree += 1
        curtree -= 1
        action = OpenedFilesCommand.trees[curtree].get_action(row - prevlength)
        if action is None:
            return
        if 'id' in action:
            node = OpenedFilesCommand.trees[curtree].nodes[action['id']]
        goto_linenumber = row + 1
        if action['action'] == 'file' and act == 'default':
            for win in sublime.windows():
                view = first(win.views(), lambda v: v.id() == action['view_id'])
                if view:
                    focus_window(win, view)
                    break
        elif action['action'] == 'window':
            OpenedFilesCommand.trees[curtree].hidden = not OpenedFilesCommand.trees[curtree].hidden
            draw_view(window, edit, OpenedFilesCommand.trees)
        elif action['action'] == 'fold' and act != 'unfold':
            OpenedFilesCommand.trees[curtree].nodes[action['id']].status = 'unfold'
            draw_view(window, edit, OpenedFilesCommand.trees)
        elif action['action'] == 'unfold' and act != 'fold':
            OpenedFilesCommand.trees[curtree].nodes[action['id']].status = 'fold'
            draw_view(window, edit, OpenedFilesCommand.trees)
        elif act == 'fold' and node.parent is not None and node.parent != '':
            goto_linenumber = OpenedFilesCommand.trees[curtree].nodes[node.parent].stringnum
            OpenedFilesCommand.trees[curtree].nodes[node.parent].status = 'unfold'
            draw_view(window, edit, OpenedFilesCommand.trees)
        elif act == 'unfold' and node.children:
            goto_linenumber = OpenedFilesCommand.trees[curtree].nodes[sorted(node.children)[0]].stringnum
        if goto_linenumber == '':
            goto_linenumber = row + 1
        self.view.run_command("goto_line", {"line": goto_linenumber})

class OpenedFilesOpenExternalCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        selection = self.view.sel()[0]
        (row, col) = self.view.rowcol(selection.begin())
        action = OpenedFilesCommand.tree.get_action(row)
        if action is None:
            return
        node = OpenedFilesCommand.tree.nodes[action['id']]
        self.view.window().run_command("open_dir", {"dir": node.node_id})

# MOUSE ACTIONS:

def mouse_click_actions(view, args):
    s = view.settings()
    if s.get("opened_files_type"):
        view.run_command('opened_files_act') #call user defined command
    elif s.get("dired_path") and not s.get("dired_rename_mode"): #for FileBrowser plugin
        if 'directory' in view.scope_name(view.sel()[0].a):
            command = ("dired_expand", {"toggle": True})
        else:
            command = ("dired_select", {"other_group": True})
        view.run_command(*command)
    else:
        system_command = args["command"] if "command" in args else None
        if system_command:
            system_args = dict({"event": args["event"]}.items())
            system_args.update(dict(args["args"].items()))
            view.run_command(system_command, system_args)

if ST3:
    class MouseDoubleclickCommand(sublime_plugin.TextCommand):
        def run_(self, view, args):
            mouse_click_actions(self.view, args)
else:
    class MouseDoubleclickCommand(sublime_plugin.TextCommand):
        def run_(self, args):
            mouse_click_actions(self.view, args)

# Event listners

def get_opened_files_view():
    windows = sublime.windows()
    for win in windows:
        views = win.views()
        if OpenedFilesCommand.OPENED_FILES_VIEW is not None:
            view = first(views, lambda v: v.id() == OpenedFilesCommand.OPENED_FILES_VIEW)
        else:
            view = first(views, lambda v: v.settings().get("opened_files_type"))
        if view:
            return view
    return None

def update_opened_files_view(other_window=False):
    view = get_opened_files_view()
    if view:
        view.run_command('opened_files', {"other_window": other_window})

def is_transient_view(window, view): # from https://github.com/FichteFoll/FileHistory (MIT license)
    if not ST3:
        return False

    if window.get_view_index(view)[1] == -1:
        # If the view index is -1, then this can't be a real view.
        # window.transient_view_in_group is not returning the correct
        # value when we quickly cycle through the quick panel previews.
        return True
    return view == window.transient_view_in_group(window.active_group())

class OpenedFilesListener(sublime_plugin.EventListener):
    current_view = None
    current_window = None
    active_list = {}

    def on_activated(self, view): #save last opened documents or dired view
        settings = view.settings()
        if settings.get("opened_files_type"):
            OpenedFilesListener.current_window = view.window()
        if settings.get("opened_files_type") or settings.get('dired_path'):
            self.current_view = view
            return
        if OpenedFilesListener.current_window == view.window() and not view.id() in OpenedFilesListener.active_list:
            OpenedFilesListener.active_list[view.id()] = True
            self.on_new(view)

    def on_close(self, view):
        w = sublime.active_window()
        if w != OpenedFilesListener.current_window or is_transient_view(w, view) and not view.id() in OpenedFilesListener.active_list:
            update_opened_files_view(True)
            return
        if view.id() in OpenedFilesListener.active_list:
            OpenedFilesListener.active_list[view.id()] = False
        if not 'opened_files' in view.scope_name(0):
            update_opened_files_view()
            return
        OpenedFilesListener.current_window = None #reset current window
        # check if closed view was a single one in group
        if ST3:
            single = not w.views_in_group(0) or not w.views_in_group(1)
        else:
            single = ([view.id()] == [v.id() for v in w.views_in_group(0)] or
                      [view.id()] == [v.id() for v in w.views_in_group(1)])
        if w.num_groups() == 2 and single:
            # without timeout ST may crash
            sublime.set_timeout(lambda: w.set_layout({"cols": [0.0, 1.0], "rows": [0.0, 1.0], "cells": [[0, 0, 1, 1]]}), 300)

    def on_new(self, view):
        opened_view = get_opened_files_view()
        w = sublime.active_window()
        if w != OpenedFilesListener.current_window or not opened_view or is_transient_view(w, view):
            update_opened_files_view(True)
            return
        active_view = w.active_view()
        num_groups = w.num_groups()
        if num_groups >= 2:
            for i in range(0, num_groups):
                if not is_any_opened_files_in_group(w, i):
                    w.focus_view(self.current_view) #focus on dired/opened documents view to prevent from strange views' switching
                    w.set_view_index(view, i, len(w.views_in_group(i)))
                    w.focus_view(view)
                    break
        update_opened_files_view()

    def on_load(self, view):
        w = sublime.active_window()
        if w != OpenedFilesListener.current_window:
            update_opened_files_view(True)
            return
        self.on_new(view)

    def on_clone(self, view):
        w = sublime.active_window()
        if w != OpenedFilesListener.current_window:
            update_opened_files_view(True)
            return
        self.on_new(view)

    def on_post_save_async(self, view):
        w = sublime.active_window()
        if w != OpenedFilesListener.current_window:
            update_opened_files_view(True)
            return
        self.on_new(view)

def plugin_loaded(): #this function autoruns on plugin loaded
    view = get_opened_files_view()
    if view is not None:
        view.run_command('opened_files')
        window = view.window()
        OpenedFilesListener.current_window = window
        for v in window.views():
            settings = v.settings()
            if settings.get("opened_files_type") or settings.get('dired_path'):
                continue
            if not v.id() in OpenedFilesListener.active_list:
                OpenedFilesListener.active_list[v.id()] = True

def is_any_opened_files_in_group(window, group):
    syntax = 'Packages/OpenedFiles/opened_files%s' % SYNTAX_EXTENSION
    return any(v.settings().get('syntax') == syntax for v in window.views_in_group(group))
