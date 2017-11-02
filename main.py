#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

import sublime
import sublime_plugin

VERSION_MAJOR = 0
VERSION_MINOR = 0
VERSION_REVISION = 2

ST3 = int(sublime.version()) >= 3000

if ST3:
    from .show import show
else:  # ST2 imports
    from show import show

def debug(level, *args):
	if level <= KateDocumentsCommand.debug_level:
		print('[DEBUG]', level, args)

class KateDocumentsCommand(sublime_plugin.TextCommand):

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

	def get_path(self, view_list):	
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
		for filename in filenames:
			for i in range(0, len(filename)):
				if len(lasttree) > i and lasttree[i] == filename[i]:
					continue
				result += self.separator*i + filename[i] + '\n'
			lasttree = filename
		return result, maxtree, filenames

	def run(self, edit):
		# self.view.insert(edit, 0, "Hello, World!")
		window = self.view.window()
		view_list = window.views()
		result, maxtree, filenames = self.get_path(view_list)

		#From ST FileBrowser
		view = show(window, os.sep . join(maxtree), other_group=True)
		view.erase(edit, sublime.Region(0, view.size())) #clear view content
		view.insert(edit, 0, result) #paste result string
		window.focus_view(view)
