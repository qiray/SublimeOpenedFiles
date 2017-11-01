
import os

import sublime
import sublime_plugin

VERSION_MAJOR = 0
VERSION_MINOR = 0
VERSION_REVISION = 2

class KateDocumentsCommand(sublime_plugin.TextCommand):

	separator = '  '
	untitled_name = 'untitled' #const
	debug_level = 1

	@staticmethod
	def debug(level, *args):
		if level <= KateDocumentsCommand.debug_level:
			print('[DEBUG]', level, args)

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

	def run(self, edit):
		# self.view.insert(edit, 0, "Hello, World!")
		view_list = self.view.window().views()
		filenames = []
		maxtree = []
		is_shorten = False
		for view in view_list:
			name = self.view_name(view)
			self.debug(10, name)
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
		self.debug(1, maxtree)
		for i in range(0, len(filenames)):
			if len(filenames[i]) > len(maxtree):
				filenames[i] = filenames[i][len(maxtree):]
		filenames = sorted(filenames)
		self.debug(5, filenames)
		result = ''
		lasttree = []
		for filename in filenames:
			for i in range(0, len(filename)):
				if len(lasttree) > i and lasttree[i] == filename[i]:
					continue
				result += self.separator*i + filename[i] + '\n'
			lasttree = filename
		print(result, '')
