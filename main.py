#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

import sublime
import sublime_plugin

VERSION_MAJOR = 0
VERSION_MINOR = 0
VERSION_REVISION = 3

ST3 = int(sublime.version()) >= 3000
KATE_DOCUMENTS_VIEW = None

if ST3:
    from .show import show, first
    from .nodetree import Tree
else:  # ST2 imports
    from show import show, first
    from nodetree import Tree

tree = Tree()

def debug(level, *args):
    if level <= KateDocumentsCommand.debug_level:
        print('[DEBUG]', level, args)

def view_name(view):
    result = KateDocumentsCommand.untitled_name
    filename = view.file_name()
    name = view.name()
    if filename is not None and filename != '':
        result = filename
    elif name is not None and name != '':
        result = name
    return result

def generate_tree(view_list):
    localtree = Tree()
    for view in view_list:
        name = view_name(view)
        localtree.add_filename(name, view.id(), is_file=False if view.file_name() is None else True)
    return localtree

def draw_tree(window, edit, tree):
    global KATE_DOCUMENTS_VIEW

    view = show(window, 'Documents', view_id=KATE_DOCUMENTS_VIEW, other_group=True)
    if not view:
        KATE_DOCUMENTS_VIEW = None
        return
    KATE_DOCUMENTS_VIEW = view.id()
    view.set_read_only(False) #Enable edit for pasting result
    view.erase(edit, sublime.Region(0, view.size())) #clear view content
    view.insert(edit, 0, str(tree)) #paste result tree
    view.set_read_only(True) #Disable edit

class KateDocumentsCommand(sublime_plugin.TextCommand): #view.run_command('kate_documents')

    untitled_name = 'untitled' #const
    debug_level = 1

    def run(self, edit):
        global KATE_DOCUMENTS_VIEW
        global tree
        window = self.view.window()
        view_list = window.views()

        temp = []
        for view in view_list:
            s = view.settings()
            if s.get("kate_documents_type"):
                KATE_DOCUMENTS_VIEW = view.id()
            elif s.get('dired_path'):
                pass
            else:
                temp.append(view)
        view_list = temp

        tree = generate_tree(view_list)
        draw_tree(window, edit, tree)

#TODO: make 1 class/command for all actions - fold/unfold and open
#TODO: make correct cursor moving
#TODO: open file browser or any default app on "/" pressed

class KateDocumentsActCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        selection = self.view.sel()[0]
        self.open_file(edit, selection)

    def open_file(self, edit, selection):
        global tree
        window = self.view.window()
        (row, col) = self.view.rowcol(selection.begin())

        action = tree.get_action(row)
        if action is None:
            return
        if action['action'] == 'file':
            view = first(window.views(), lambda v: v.id() == action['view_id'])
            window.focus_view(view)
        elif action['action'] == 'fold':
            tree.nodes[action['id']].status = 'unfold'
            draw_tree(window, edit, tree)
        elif action['action'] == 'unfold':
            tree.nodes[action['id']].status = 'fold'
            draw_tree(window, edit, tree)
        self.view.run_command("goto_line", {"line": row + 1})

class KateDocumentsFoldCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global tree
        selection = self.view.sel()[0]
        window = self.view.window()
        (row, col) = self.view.rowcol(selection.begin())
        action = tree.get_action(row)
        if action is None:
            return
        if action['action'] == 'file':
            node = tree.nodes[action['id']]
            if node.parent is not None:
                tree.nodes[node.parent].status = 'unfold'
                draw_tree(window, edit, tree)
        elif action['action'] == 'fold':
            tree.nodes[action['id']].status = 'unfold'
            draw_tree(window, edit, tree)
        if row != 0:
            self.view.run_command("goto_line", {"line": row})

class KateDocumentsUnfoldCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global tree
        selection = self.view.sel()[0]
        window = self.view.window()
        (row, col) = self.view.rowcol(selection.begin())
        action = tree.get_action(row)
        if action is None:
            return
        if action['action'] == 'file':
            node = tree.nodes[action['id']]
            if node.parent is not None:
                tree.nodes[node.parent].status = 'fold'
                draw_tree(window, edit, tree)
        elif action['action'] == 'unfold':
            tree.nodes[action['id']].status = 'fold'
            draw_tree(window, edit, tree)
        self.view.run_command("goto_line", {"line": row + 2})

class OpenedDocumentsNoopCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        pass

# MOUSE ACTIONS ##############################################

def mouse_click_actions(view, args):
    s = view.settings()
    if s.get("kate_documents_type"):
        view.run_command('kate_documents_act') #call user defined command
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

#TODO: add event listener for open/close/new tabs
# class SampleListener(sublime_plugin.EventListener):
#     def on_load(self, view):
#         view.run_command('kate_documents')

#     def on_pre_close(self, view):
#         print('Closing!' + view.name())
#         s = view.settings()`
#         if not s.get("kate_documents_type"):
#             view.run_command('kate_documents')
