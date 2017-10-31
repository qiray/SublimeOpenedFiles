
import sublime
import sublime_plugin


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
		for view in view_list:
			self.view.insert(edit, 0, self.view_name(view) + '\n')
