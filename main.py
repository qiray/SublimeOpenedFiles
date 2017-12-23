#!/usr/bin/python
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin

VERSION_MAJOR = 0
VERSION_MINOR = 1
VERSION_REVISION = 0

ST3 = int(sublime.version()) >= 3000
OPENED_FILES_VIEW = None

#TODO: open/reopen files in other tab
#TODO: prevent from showing filebrowser view when open/reopen
#TODO: show files after all filetrees
#TODO: add listview along with treeview (like in Atom editor)
#TODO: add max depth (like in Kate editor)
#TODO: goto line with new opened file

if ST3:
    from .show import show, first
    from .nodetree import Tree
else:  # ST2 imports
    from show import show, first
    from nodetree import Tree

tree = Tree()

def debug(level, *args):
    if level <= OpenedFilesCommand.debug_level:
        print('[DEBUG]', level, args)

def view_name(view):
    result = OpenedFilesCommand.untitled_name
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

def draw_tree(window, edit, tree):
    global OPENED_FILES_VIEW

    view = show(window, 'Documents', view_id=OPENED_FILES_VIEW, other_group=True)
    if not view:
        OPENED_FILES_VIEW = None
        return
    OPENED_FILES_VIEW = view.id()
    view.set_read_only(False) #Enable edit for pasting result
    view.erase(edit, sublime.Region(0, view.size())) #clear view content
    view.insert(edit, 0, str(tree)) #paste result tree
    view.set_read_only(True) #Disable edit

class OpenedFilesCommand(sublime_plugin.TextCommand): #view.run_command('opened_files')
    
    untitled_name = 'untitled' #const
    debug_level = 1

    def run(self, edit):
        global OPENED_FILES_VIEW
        global tree
        window = self.view.window()
        view_list = window.views()

        temp = []
        for view in view_list:
            settings = view.settings()
            if settings.get("opened_files_type"):
                OPENED_FILES_VIEW = view.id()
            elif settings.get('dired_path'):
                pass
            else:
                temp.append(view)
        view_list = temp

        tree = generate_tree(view_list, tree)
        draw_tree(window, edit, tree)

class OpenedFilesActCommand(sublime_plugin.TextCommand):
    def run(self, edit, act='default'):
        selection = self.view.sel()[0]
        self.open_file(edit, selection, act)

    def open_file(self, edit, selection, act):
        global tree
        window = self.view.window()
        (row, col) = self.view.rowcol(selection.begin())

        action = tree.get_action(row)
        if action is None:
            return
        node = tree.nodes[action['id']]
        goto_linenumber = row + 1
        if action['action'] == 'file' and act == 'default':
            view = first(window.views(), lambda v: v.id() == action['view_id'])
            window.focus_view(view)
        elif action['action'] == 'fold' and act != 'unfold':
            tree.nodes[action['id']].status = 'unfold'
            draw_tree(window, edit, tree)
        elif action['action'] == 'unfold' and act != 'fold':
            tree.nodes[action['id']].status = 'fold'
            draw_tree(window, edit, tree)
        elif act == 'fold' and node.parent is not None and node.parent != '':
            goto_linenumber = tree.nodes[node.parent].stringnum
            tree.nodes[node.parent].status = 'unfold'
            draw_tree(window, edit, tree)
        elif act == 'unfold' and node.children:
            goto_linenumber = tree.nodes[sorted(node.children)[0]].stringnum
        if goto_linenumber == '':
            goto_linenumber = row + 1
        self.view.run_command("goto_line", {"line": goto_linenumber})

class OpenedFilesOpenExternalCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        selection = self.view.sel()[0]
        (row, col) = self.view.rowcol(selection.begin())
        action = tree.get_action(row)
        if action is None:
            return
        node = tree.nodes[action['id']]
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
        if OPENED_FILES_VIEW is not None:
            view = first(views, lambda v: v.id() == OPENED_FILES_VIEW)
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
    def on_close(self, view):
        update_opened_files_view()

    def on_new(self, view):
        print(0)
        update_opened_files_view()

    def on_load(self, view):
        print(1)
        update_opened_files_view()

    def on_clone(self, view):
        print(2)
        update_opened_files_view()

def plugin_loaded(): #this function autoruns on plugin loaded
    view = get_opened_files_view()
    if view is not None:
        view.run_command('opened_files')
