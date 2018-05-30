#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sublime
import re

ST3 = int(sublime.version()) >= 3000

class Node(object):
    separator = '  '

    def __init__(self, node_id, children, status, parent=None, view_id=None):
        self.node_id = node_id
        self.parent = parent
        self.children = children
        self.status = status
        self.view_id = view_id
        self.stringnum = ''
        self.max_parents = []
        self.printed = False

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
    tree_view = False

    def __init__(self, name = ""):
        self.name = name
        self.hidden = False #if True then hide this window's tree
        self.nodes = {}
        self.parents = {}
        self.opened_views = {}
        self.actions_map = ActionsMap()
        self.size = 0

    def get_nodes(self):
        return self.nodes

    def get_node(self, node_id):
        if node_id in self.nodes:
            return self.nodes[node_id]
        return None

    def set_node(self, node_id, node):
        self.nodes[node_id] = node

    def add_filename(self, filename, view_id, is_file):
        arr = filename.split(os.sep)
        length = len(arr)
        if not is_file:
            newname = '{} (id = {})'.format(filename, view_id)
            node = Node(newname, {}, 'file', None, view_id)
            self.nodes[newname] = node
            self.opened_views[newname] = node
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
                    self.nodes[name] = Node(name, {child : True}, 'fold', os.sep.join(arr[:i - 1]))
            else:
                self.nodes[name] = Node(name, {}, 'file', os.sep.join(arr[:i - 1]), view_id)

    def draw_list(self, result):
        stringnum = 1
        length = 0 if self.name == '' else 1
        nodes = sorted(self.nodes)
        nodes.sort(key=lambda x: x.split(os.sep)[-1]) #sort by short filenames
        for name in nodes:
            node = self.nodes[name]
            if node.view_id:
                temp, stringnum = node.print_children(self.nodes, self.actions_map, length, stringnum)
                result += temp
            self.size = stringnum
        return result

    def prepare_default_tree(self, printed_parents):
        result = []
        for name in printed_parents:
            tempname = name
            flag = True
            while len(self.nodes[tempname].children) == 1:
                tempname = sorted(self.nodes[tempname].children)[0]
                if self.nodes[tempname].status == 'file':
                    tempname = self.nodes[tempname].parent
                    result.append(tempname)
                    flag = False
                    break
            if flag:
                result.append(tempname)
        result.sort(key=lambda x: x.split(os.sep)[-1].lower())
        return result

    def prepare_notfull_tree(self, printed_parents):
        result = []
        while len(printed_parents) == 1:
            key = printed_parents[0]
            result = sorted(self.nodes[key].children)
            result.sort(key=lambda x: self.nodes[x].status == 'file')
            flag = False
            for filename in result:
                if self.nodes[filename].status == 'file':
                    flag = True
                    break
            if flag:
                break
            printed_parents = result
        return printed_parents    

    def draw_tree(self, result):
        printed_parents = sorted(self.parents) #dict here becomes list!
        printed_parents.sort(key=lambda x: self.nodes[x].status == 'file')
        if Tree.tree_size != 'default' and Tree.tree_size != 'full' and Tree.tree_size != 'medium':
            Tree.tree_size = 'default'
        if Tree.tree_size != 'full':
            printed_parents = self.prepare_notfull_tree(printed_parents)
        if Tree.tree_size == 'default':
            printed_parents = self.prepare_default_tree(printed_parents)
        stringnum = 1
        length = 0 if self.name == '' else 1
        for name in printed_parents:
            temp, stringnum = self.nodes[name].print_children(self.nodes, self.actions_map, length, stringnum)
            result += temp
        for name in self.opened_views:
            temp, stringnum = self.opened_views[name].print_children(self.opened_views, self.actions_map, length, stringnum)
            result += temp
        self.size = stringnum
        return result

    def __str__(self):
        self.actions_map.clear()
        self.actions_map.set_window_action()
        if self.hidden:
            return '▸ ' +  self.name
        result = '▾ ' +  self.name
        plugin_settings = sublime.load_settings('opened_files.sublime-settings')
        Tree.tree_size = plugin_settings.get('tree_size')
        Tree.tree_view = plugin_settings.get('tree_view')
        if not Tree.tree_view:
            return self.draw_list(result)
        return self.draw_tree(result)

    def get_action(self, number):
        return self.actions_map.get_action(number)

class ActionsMap(object):

    def __init__(self):
        self.map = {}
        self.count = 0

    def set_window_action(self):
        self.map[0] = {'action' : "window"}

    def add_action(self, node):
        self.count += 1
        self.map[self.count] = {'action' : node.status, 'id' : node.node_id, 'view_id' : node.view_id}

    def get_action(self, number):
        if number in self.map:
            return self.map[number]
        return None

    def clear(self):
        self.map = {}
        self.count = 0
