#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import sublime

ST3 = int(sublime.version()) >= 3000

separator = '  '

class Node(object):

    def __init__(self, node_id, children, status, parent=None, view_id=None):
        self.node_id = node_id
        self.parent = parent
        self.children = children
        self.status = status
        self.view_id = view_id

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
        result = separator*length + self.get_name() + '\n'
        self.stringnum = stringnum
        stringnum += 1
        actions_map.add_action(self)
        if self.status == 'unfold':
            return result, stringnum
        children = sorted(self.children)
        for child in children:
            temp, stringnum = array[child].print_children(array, actions_map, length + 1, stringnum)
            result += temp
        return result, stringnum

class Tree(object):

    def __init__(self):
        self.nodes = {}
        self.parents = {}
        self.actions_map = ActionsMap()

    def add_filename(self, filename, view_id, is_file):
        arr = filename.split(os.sep)
        length = len(arr)
        if not is_file:
            newname = '{} (id = {})'.format(filename, view_id)
            self.nodes[newname] = Node(newname, {}, 'file', None, view_id)
            self.parents[newname] = True
            return
        if arr[0] == '':
            arr[0] = os.sep
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

    def __str__(self):
        result = ''
        self.actions_map.clear()
        printed_parents = sorted(self.parents) #dict here becomes list!
        while len(printed_parents) == 1:
            key = printed_parents[0]
            templist = sorted(self.nodes[key].children)
            flag = False
            for filename in templist:
                if self.nodes[filename].status == 'file':
                    flag = True
                    break
            if flag:
                break
            printed_parents = templist
        stringnum = 1
        for name in printed_parents:
            temp, stringnum = self.nodes[name].print_children(self.nodes, self.actions_map, 0, stringnum)
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
