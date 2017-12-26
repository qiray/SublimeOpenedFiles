#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sublime

ST3 = int(sublime.version()) >= 3000

class Element(object):

    def __init__(self, name, node_id):
        self.node_id = node_id
        self.name = name
        self.stringnum = 0

    def get_name(self):
        return '≡ '+ self.name

class List(object):

    def __init__(self):
        self.views = {}

    def add_filename(self, filename, view_id, is_file):
        arr = filename.split(os.sep)
        name = arr[-1]
        if not is_file:
            newname = '{} (id = {})'.format(filename, view_id)
            self.views[newname] = Element(newname, view_id)
            return
        self.views[name] = Element(name, view_id)

    def __str__(self):
        result = ''
        templist = sorted(self.views)
        stringnum = 1
        for node in templist:
            result += '≡ ' + self.views[node].name + "\n"
            self.views[node].stringnum = stringnum
            stringnum += 1
        return result

    def get_view_id(self, stringnum):
        for elm in self.views:
            if self.views[elm].stringnum == stringnum:
                return self.views[elm].node_id
        return None
