"""Functions from sublime-goto-window plugin - https://github.com/ccampbell/sublime-goto-window"""

import os
import sublime
import sublime_plugin
from subprocess import Popen, PIPE

def focus_window(window, view):
    focus(window, view)
    # OS X and Linux require specific workarounds to activate a window
    # due to this bug:
    # https://github.com/SublimeTextIssues/Core/issues/444
    if sublime.platform() == 'osx':
        _osx_focus()
    elif sublime.platform() == 'linux':
        _linux_focus(window, view)

def focus(window, view):
    active_group = window.active_group()

    # In Sublime Text 2 if a folder has no open files in it the active view
    # will return None. This tries to use the actives view and falls back
    # to using the active group

    # Calling focus then the command then focus again is needed to make this
    # work on Windows
    if view is not None:
        window.focus_view(view)
        window.run_command('focus_neighboring_group')
        window.focus_view(view)
        return

    if active_group is not None:
        window.focus_group(active_group)
        window.run_command('focus_neighboring_group')
        window.focus_group(active_group)

def _osx_focus():
    name = 'Sublime Text'
    if int(sublime.version()) < 3000:
        name = 'Sublime Text 2'

    # This is some magic. I spent many many hours trying to find a
    # workaround for the Sublime Text bug. I found a bunch of ugly
    # solutions, but this was the simplest one I could figure out.
    #
    # Basically you have to activate an application that is not Sublime
    # then wait and then activate sublime. I picked "Dock" because it
    # is always running in the background so it won't screw up your
    # command+tab order. The delay of 1/60 of a second is the minimum
    # supported by Applescript.
    cmd = """
        tell application "System Events"
            activate application "Dock"
            delay 1/60
            activate application "%s"
        end tell""" % name

    Popen(['/usr/bin/osascript', "-e", cmd], stdout=PIPE, stderr=PIPE)

# Focus a Sublime window using wmctrl. wmctrl takes the title of the window
# that will be focused, or part of it.
def _linux_focus(window, view):
    project = get_project(view)
    window_title = get_official_title(view, project)
    print (window_title)
    try:
        Popen(["wmctrl", "-a", window_title],
                stdout=PIPE, stderr=PIPE)
    except FileNotFoundError:
        msg = "`wmctrl` is required by GotoWindow but was not found on " \
              "your system. Please install it and try again."
        sublime.error_message(msg)


"""
Functions from https://github.com/gwenzek/SublimeSetWindowTitle
"""

def get_official_title(view, project):
    """Returns the official name for a given view.
    Note: The full file path isn't computed,
    because ST uses `~` to shorten the path.
    """
    print(1, 2)
    view_name = view.name() or view.file_name() or "untitled"
    print (view_name)
    official_title = os.path.basename(view_name)
    print (official_title)
    if view.is_dirty():
        official_title += " •"
    if project:
        official_title += " (%s)" % project
    official_title += " - Sublime Text"
    return official_title

def get_project(view):
    project = None
    window = view.window()
    if not window:
        return
    project = window.project_file_name()
    if not project:
        folders = window.folders()
        project = folders[0] if folders else None
    if project:
        project = os.path.basename(project)
        project = os.path.splitext(project)[0]
    return project
