#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import sublime
from os.path import basename

ST3 = int(sublime.version()) >= 3000

separator = '  '

class Node:

    def __init__(self, id, children, status):
        self.id = id
        self.children = children
        self.status = status

    def add_child(self, child):
        if not child in self.children:
            self.children[child] = True

    def get_name(self):
        arr = self.id.split(os.sep)
        if self.status == 'unfold':
            return '▸ ' + arr[-1]
        elif self.status == 'fold':
            return '▾ ' + arr[-1]
        return '≡ '+ arr[-1]

    def print_children(self, array, actions_map, length):
        result = separator*length + self.get_name() + '\n'
        actions_map.add_action(self)
        if self.status == 'unfold':
            return result
        children = sorted(self.children)
        for child in children:
            result += array[child].print_children(array, actions_map, length + 1)
        return result

class Tree:

    def __init__(self):
        self.nodes = {}
        self.parents = {}
        self.actions_map = ActionsMap()

    def add_filename(self, filename):
        arr = filename.split(os.sep)
        length = len(arr)
        if not arr[0] in self.parents:
            self.parents[arr[0]] = True
        for i in range(1, length + 1):
            name = os.sep.join(arr[:i])
            if i != length:
                child = os.sep.join(arr[:i + 1])
                if name in self.nodes:
                    self.nodes[name].add_child(child)
                else:
                    self.nodes[name] = Node(name, {child : True}, 'fold')
            else:
                self.nodes[name] = Node(name, {}, 'file')

    def __str__(self): #TODO: draw filetree via this method - not current get_path function
        result = ''
        self.actions_map.clear()
        printed_parents = sorted(self.parents) #dict here becomes list!
        while len(printed_parents) == 1:
            key = printed_parents[0]
            templist = sorted(self.nodes[key].children)
            flag = False
            for file in templist:
                if self.nodes[file].status == 'file':
                    flag = True
                    break
            if flag:
                break
            printed_parents = templist
        for name in printed_parents:
            result += self.nodes[name].print_children(self.nodes, self.actions_map, 0)
        return result

    def get_action(self, number):
        return self.actions_map.get_action(number)

class ActionsMap:

    def __init__(self):
        self.map = {}
        self.count = 0

    def add_action(self, node):
        self.map[self.count] = {'action' : node.status, 'id' : node.id}
        self.count += 1

    def get_action(self, number):
        if number in self.map:
            return self.map[number]
        return None

    def clear(self):
        self.map = {}
        self.count = 0
