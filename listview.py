#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sublime

ST3 = int(sublime.version()) >= 3000

class Element(object):
    """This is an object representing view storing in listview"""
    def __init__(self, name, node_id, window):
        self.node_id = node_id
        self.name = name
        self.window = window
        self.stringnum = 0

    def get_name(self):
        """Return view name"""
        return '≡ '+ self.name

class List(object):
    """Object for storing and showing views in listview mode"""
    def __init__(self):
        self.views = {}

    def add_filename(self, filename, view_id, is_file, window):
        """
        Function to add view into the list
        is_file param is used to differ opened files from nonfile views
        """
        arr = filename.split(os.sep)
        name = arr[-1]
        if not is_file:
            newname = '{} (id = {})'.format(filename, view_id)
            self.views[newname] = Element(newname, view_id, window)
            return
        self.views[name] = Element(name, view_id, window)

    def __str__(self):
        """Function to draw listview"""
        result = ''
        templist = sorted(self.views)
        templist.sort(key=lambda x: self.views[x].window.id())
        stringnum = 1
        win_id = 0
        prev_id = 1
        for node in templist:
            win_id = self.views[node].window.id()
            if win_id != prev_id:
                result += "Hm.\n"
                stringnum += 1
            prev_id = win_id
            result += '≡ ' + self.views[node].name + "\n"
            self.views[node].stringnum = stringnum
            stringnum += 1
        return result

    def get_action(self, stringnum):
        """Get action by string number"""
        for elm in self.views:
            if self.views[elm].stringnum == stringnum:
                return self.views[elm].node_id
        return None

    def get_view_id(self, stringnum):
        """Get action by string number"""
        for elm in self.views:
            if self.views[elm].stringnum == stringnum:
                return self.views[elm].node_id
        return None
