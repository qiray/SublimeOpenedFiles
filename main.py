#!/usr/bin/python
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin

VERSION_MAJOR = 0
VERSION_MINOR = 1
VERSION_REVISION = 1

ST3 = int(sublime.version()) >= 3000

#TODO: add comments
#TODO: add max depth (like in Kate editor)
#TODO: add settings
#TODO: test plugin in right group

if ST3:
    from .common import untitled_name, debug, SYNTAX_EXTENSION
    from .show import show, first
    from .treeview import Tree
    from .listview import List
else:  # ST2 imports
    from common import untitled_name, debug, SYNTAX_EXTENSION
    from show import show, first
    from treeview import Tree
    from listview import List

def view_name(view):
    result = untitled_name
    filename = view.file_name()
    name = view.name()
    if filename is not None and filename != '':
        result = filename
    elif name is not None and name != '':
        result = name
    return result

def generate_tree(view_list, localtree):
    result = Tree()
    for view in view_list:
        name = view_name(view)
        result.add_filename(name, view.id(), is_file=False if view.file_name() is None else True)
    nodes = result.get_nodes()
    for n in nodes:
        old_node = localtree.get_node(n)
        new_node = result.get_node(n)
        if old_node:
            new_node.status = old_node.status
            result.set_node(n, new_node)
    return result

def generate_list(view_list):
    result = List()
    for view in view_list:
        name = view_name(view)
        result.add_filename(name, view.id(), is_file=False if view.file_name() is None else True)
    return result

def draw_view(window, edit, view_object):

    view = show(window, 'Documents', view_id=OpenedFilesCommand.OPENED_FILES_VIEW, other_group=True)
    if not view:
        OpenedFilesCommand.OPENED_FILES_VIEW = None
        return
    OpenedFilesCommand.OPENED_FILES_VIEW = view.id()
    view.set_read_only(False) #Enable edit for pasting result
    view.erase(edit, sublime.Region(0, view.size())) #clear view content
    view.insert(edit, 0, str(view_object)) #paste result
    view.set_read_only(True) #Disable edit

class OpenedFilesCommand(sublime_plugin.TextCommand): #view.run_command('opened_files')

    OPENED_FILES_VIEW = None
    tree = Tree()
    files_list = List()

    def run(self, edit):
        window = self.view.window()
        view_list = window.views()

        temp = []
        for view in view_list:
            settings = view.settings()
            if settings.get("opened_files_type"):
                OpenedFilesCommand.OPENED_FILES_VIEW = view.id()
            elif settings.get('dired_path'):
                pass
            else:
                temp.append(view)
        view_list = temp

        plugin_settings = sublime.load_settings('opened_files.sublime-settings')
        if plugin_settings.get('tree_view'): #treeview
            OpenedFilesCommand.tree = generate_tree(view_list, OpenedFilesCommand.tree)
            draw_view(window, edit, OpenedFilesCommand.tree)
        else: #listview
            OpenedFilesCommand.files_list = generate_list(view_list)
            draw_view(window, edit, OpenedFilesCommand.files_list)

class OpenedFilesActCommand(sublime_plugin.TextCommand):
    def run(self, edit, act='default'):
        selection = self.view.sel()[0]
        self.open_file(edit, selection, act)

    def open_file(self, edit, selection, act):
        window = self.view.window()
        (row, col) = self.view.rowcol(selection.begin())

        plugin_settings = sublime.load_settings('opened_files.sublime-settings')
        if not plugin_settings.get('tree_view'): #list view
            view_id = OpenedFilesCommand.files_list.get_view_id(row + 1)
            view = first(window.views(), lambda v: v.id() == view_id)
            window.focus_view(view)
            goto_linenumber = row + 1
            return

        action = OpenedFilesCommand.tree.get_action(row)
        if action is None:
            return
        node = OpenedFilesCommand.tree.nodes[action['id']]
        goto_linenumber = row + 1
        if action['action'] == 'file' and act == 'default':
            view = first(window.views(), lambda v: v.id() == action['view_id'])
            window.focus_view(view)
        elif action['action'] == 'fold' and act != 'unfold':
            OpenedFilesCommand.tree.nodes[action['id']].status = 'unfold'
            draw_view(window, edit, OpenedFilesCommand.tree)
        elif action['action'] == 'unfold' and act != 'fold':
            OpenedFilesCommand.tree.nodes[action['id']].status = 'fold'
            draw_view(window, edit, OpenedFilesCommand.tree)
        elif act == 'fold' and node.parent is not None and node.parent != '':
            goto_linenumber = OpenedFilesCommand.tree.nodes[node.parent].stringnum
            OpenedFilesCommand.tree.nodes[node.parent].status = 'unfold'
            draw_view(window, edit, OpenedFilesCommand.tree)
        elif act == 'unfold' and node.children:
            goto_linenumber = OpenedFilesCommand.tree.nodes[sorted(node.children)[0]].stringnum
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
    windows = sublime.windows()#[0].views()
    for win in windows:
        views = win.views()
        if OpenedFilesCommand.OPENED_FILES_VIEW is not None:
            view = first(views, lambda v: v.id() == OpenedFilesCommand.OPENED_FILES_VIEW)
        else:
            view = first(views, lambda v: v.settings().get("opened_files_type"))
        if view:
            return view
    return None

def update_opened_files_view():
    view = get_opened_files_view()
    if view:
        view.run_command('opened_files')

class OpenedFilesListener(sublime_plugin.EventListener):
    current_view = None

    def on_activated(self, view): #save last opened documents or dired view
        settings = view.settings()
        if settings.get("opened_files_type") or settings.get('dired_path'):
            self.current_view = view

    def on_close(self, view):
        update_opened_files_view()

    def on_new(self, view):
        opened_view = get_opened_files_view()
        if not opened_view:
            return
        w = sublime.active_window()
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
        self.on_new(view)

    def on_clone(self, view):
        self.on_new(view)

def plugin_loaded(): #this function autoruns on plugin loaded
    view = get_opened_files_view()
    if view is not None:
        view.run_command('opened_files')

def is_any_opened_files_in_group(window, group):
    syntax = 'Packages/OpenedFiles/opened_files%s' % SYNTAX_EXTENSION
    return any(v.settings().get('syntax') == syntax for v in window.views_in_group(group))
