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
result, maxtree, filenames = None, None, None #TODO: save these variables in settings
actionsMap = {}

if ST3:
    from .show import show
else:  # ST2 imports
    from show import show

def debug(level, *args):
    if level <= KateDocumentsCommand.debug_level:
        print('[DEBUG]', level, args)

class KateDocumentsCommand(sublime_plugin.TextCommand): #view.run_command('kate_documents')

    separator = '  '
    untitled_name = 'untitled' #const
    debug_level = 1

    @staticmethod
    def view_name(view):
        result = KateDocumentsCommand.untitled_name
        filename = view.file_name()
        name = view.name()
        if filename is not None and filename != '':
            result = filename
        elif name is not None and name != '':
            result = name
        return result

    @staticmethod
    def get_prefix(filename, index, length):
        # ▸
        #TODO: use fold and unfold
        if index == length - 1:
            return '≡ ' 
        return '▾ '

    def get_path(self, view_list):
        global actionsMap
        filenames = []
        maxtree = []
        is_shorten = False
        for view in view_list:
            name = self.view_name(view)
            debug(10, name)
            arr = name.split(os.sep)
            for i in range(0, len(arr) - 1):
                if i >= len(maxtree):
                    if is_shorten:
                        continue
                    maxtree.append(arr[i])
                    continue
                if arr[i] != maxtree[i]:
                    is_shorten = True
                    maxtree = maxtree[:i]
                    break
            filenames.append(arr)
        debug(1, maxtree)
        for i in range(0, len(filenames)):
            if len(filenames[i]) > len(maxtree):
                filenames[i] = filenames[i][len(maxtree):]
        filenames = sorted(filenames)
        debug(5, filenames)
        result = ''
        lasttree = []
        count = 0
        for filename in filenames:
            length = len(filename)
            for i in range(0, length):
                if len(lasttree) > i and lasttree[i] == filename[i]:
                    continue
                result += self.separator*i + self.get_prefix(filename, i, length) + filename[i] + '\n'
                count += 1
            actionsMap[count - 1] = os.sep.join(maxtree) + os.sep + os.sep.join(filename)
            
            lasttree = filename
        return result, maxtree, filenames

    def run(self, edit):
        global result, maxtree, filenames #TODO: use settings instead of global variables
        global KATE_DOCUMENTS_VIEW
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

        result, maxtree, filenames = self.get_path(view_list)

        #From ST FileBrowser
        view = show(window, os.sep . join(maxtree), view_id=KATE_DOCUMENTS_VIEW, other_group=True)
        if not view:
            KATE_DOCUMENTS_VIEW = None
            return
        KATE_DOCUMENTS_VIEW = view.id()
        view.erase(edit, sublime.Region(0, view.size())) #clear view content
        view.insert(edit, 0, result) #paste result string
        # window.focus_view(view)

class KateDocumentsOpenCommand(sublime_plugin.TextCommand):
    #TODO: add map for strings and their meanings - fold/unfold directory, open file etc.
    def run(self, edit):
        (row, col) = self.view.rowcol(self.view.sel()[0].begin())
        selection = self.view.sel()[0]
        self.open_file(selection)

    def open_file(self, selection): #TODO: make dict for saving full names for each string of result (global variable)
        window = self.view.window()
        (row, col) = self.view.rowcol(selection.begin())
        filename = self.view.substr(self.view.line(selection))
        if row in actionsMap:
            window.open_file(actionsMap[row])

# MOUSE ACTIONS ##############################################

def mouse_click_actions(view, args): #TODO: fix and use
    s = view.settings()
    if s.get("kate_documents_type"):
        view.run_command('kate_documents_open') #call user defined command
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
