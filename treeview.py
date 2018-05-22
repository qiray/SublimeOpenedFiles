#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sublime
import re

ST3 = int(sublime.version()) >= 3000

class Node(object):
    separator = '  '

    def __init__(self, node_id, children, status, parent=None, view_id=None, win_id=0):
        self.node_id = node_id
        self.parent = parent
        self.children = children
        self.status = status
        self.view_id = view_id
        self.stringnum = ''
        self.printed = False
        self.win_id = win_id

    def add_child(self, child):
        if not child in self.children:
            self.children[child] = True

    def get_name(self):
        arr = self.node_id.split(os.sep)
        if arr[-1] == '':
            arr[-1] = os.sep
        if self.status == 'unfold':
            return '▸ ' + arr[-1]
        elif self.status == 'fold':
            return '▾ ' + arr[-1]
        return '≡ '+ arr[-1]

    def print_children(self, array, actions_map, length, stringnum):
        result = Node.separator*length + self.get_name() + '\n'
        self.stringnum = stringnum
        stringnum += 1
        actions_map.add_action(self)
        if self.status == 'unfold':
            return result, stringnum
        children = sorted(self.children)
        children.sort(key=lambda x: array[x].status == 'file')
        for child in children:
            temp, stringnum = array[child].print_children(array, actions_map, length + 1, stringnum)
            result += temp
        return result, stringnum

class Tree(object):
    tree_size = 0

    def __init__(self):
        self.nodes = {}
        self.parents = {}
        self.opened_views = {}
        self.actions_map = ActionsMap()
        plugin_settings = sublime.load_settings('opened_files.sublime-settings')
        self.tree_view = plugin_settings.get('tree_view')
        self.windows = {}
        windows = sublime.windows()
        count = 0
        for win in windows:
            count += 1
            self.windows[win.id()] = "Window {}".format(count)

    def get_nodes(self):
        return self.nodes

    def get_node(self, node_id):
        if node_id in self.nodes:
            return self.nodes[node_id]
        return None

    def set_node(self, node_id, node):
        self.nodes[node_id] = node

    def add_filename(self, filename, view_id, is_file, window):
        win_id = window.id()
        filename = self.windows[window.id()] + os.sep + filename
        arr = filename.split(os.sep)
        length = len(arr)
        if not is_file:
            filename = '{} (id = {})'.format(filename, view_id)
            node = Node(filename, {}, 'file', None, view_id, win_id=win_id)
            self.nodes[filename] = node
            self.opened_views[filename] = node
            return
        if not arr[0] in self.parents:
            self.parents[arr[0]] = True
        for i in range(1, length + 1):
            name = os.sep.join(arr[:i])
            if i != length:
                child = os.sep.join(arr[:i + 1])
                if name in self.nodes:
                    self.nodes[name].add_child(child)
                else:
                    self.nodes[name] = Node(name, {child : True}, 'fold', os.sep.join(arr[:i - 1]), win_id=win_id)
            else:
                self.nodes[name] = Node(name, {}, 'file', os.sep.join(arr[:i - 1]), view_id, win_id=win_id)

    def __str__(self):
        result = ''
        self.actions_map.clear()
        printed_parents = sorted(self.parents) #dict here becomes list!
        printed_parents.sort(key=lambda x: self.nodes[x].status == 'file')
        plugin_settings = sublime.load_settings('opened_files.sublime-settings')
        Tree.tree_size = plugin_settings.get('tree_size')
        if Tree.tree_size != 'default' and Tree.tree_size != 'full' and Tree.tree_size != 'medium':
            Tree.tree_size = 'default'
        if Tree.tree_size != 'full':
            while len(printed_parents) == 1:
                key = printed_parents[0]
                templist = sorted(self.nodes[key].children)
                templist.sort(key=lambda x: self.nodes[x].status == 'file')
                flag = False
                for filename in templist:
                    if self.nodes[filename].status == 'file':
                        flag = True
                        break
                if flag:
                    break
                printed_parents = templist
        stringnum = 1
        if Tree.tree_size == 'default':
            templist = []
            for name in printed_parents:
                tempname = name
                flag = True
                while len(self.nodes[tempname].children) == 1:
                    tempname = sorted(self.nodes[tempname].children)[0]
                    if self.nodes[tempname].status == 'file':
                        tempname = self.nodes[tempname].parent
                        templist.append(tempname)
                        flag = False
                        break
                if flag:
                    templist.append(tempname)
            templist.sort(key=lambda x: x.split(os.sep)[-1].lower())
            printed_parents = templist
        for name in printed_parents:
            win_id = self.nodes[name].win_id
            window = self.windows[win_id]
            length = 0
            if name != window: #draw window
                node = self.nodes[window]
                result += node.get_name() + '\n'
                stringnum += 1
                self.actions_map.add_action(node)
                length = 1
                if node.status == 'unfold':
                    continue
            temp, stringnum = self.nodes[name].print_children(self.nodes, self.actions_map, length, stringnum)
            result += temp
            for name in self.opened_views: #draw non-files views
                if self.nodes[name].win_id == win_id:
                    temp, stringnum = self.opened_views[name].print_children(self.opened_views, self.actions_map, 1, stringnum)
                    result += temp
        return result

    def get_action(self, number):
        return self.actions_map.get_action(number)

class ActionsMap(object):

    def __init__(self):
        self.map = {}
        self.count = 0

    def add_action(self, node):
        self.map[self.count] = {'action' : node.status, 'id' : node.node_id, 'view_id' : node.view_id}
        self.count += 1

    def get_action(self, number):
        if number in self.map:
            return self.map[number]
        return None

    def clear(self):
        self.map = {}
        self.count = 0
