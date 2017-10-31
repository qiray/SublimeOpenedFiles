
import os

import sublime
import sublime_plugin

VERSION_MAJOR = 0
VERSION_MINOR = 0
VERSION_REVISION = 1

class KateDocumentsCommand(sublime_plugin.TextCommand):
	@staticmethod
	def view_name(view):
		if view.file_name() is not None:
			return view.file_name()
		elif view.name() is not None:
			return view.name()
		return ''

	def run(self, edit):
		# self.view.insert(edit, 0, "Hello, World!")
		view_list = self.view.window().views()
		filenames = []
		maxtree = []
		for view in view_list:
			name = self.view_name(view)
			print(name, '')
			if name == '':
				continue
			arr = name.split(os.sep)
			for i in range(0, len(arr) - 1):
				if i >= len(maxtree):
					maxtree.append(arr[i])
					continue
				if arr[i] != maxtree[i]:
					maxtree = maxtree[:i]
					break
			filenames.append(arr)
		print (maxtree, '')
		for i in range(0, len(filenames)):
			filenames[i] = filenames[i][len(maxtree):]
		print (filenames, '')
