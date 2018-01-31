# Sublime Opened Files

Plugin for Sublime Text to show opened files as a treeview:

![OpenedFiles Screenshot1](https://pp.userapi.com/c841435/v841435631/5db9a/A87MJ2pFnHc.jpg)

or a listview:

![OpenedFiles Screenshot2](https://pp.userapi.com/c841435/v841435631/5dba3/qxGQkAuE2LM.jpg)

It has different settings and also can be shown on right or left side:

![OpenedFiles Screenshot3](https://pp.userapi.com/c841435/v841435631/5dbac/NVDYqwqkLPU.jpg)

## Installation

You can install this plugin via [Sublime Package Control](https://packagecontrol.io/)

Or by cloning this repo into your SublimeText Packages directory and rename it to `OpenedFiles`.

## Settings

| Setting name     | Values       | Meaning |
| :--------------- | :----------- | :------ |
| **tree_view**    | `true` or `false`| Set `true` to show opened files as a treeview or `false` for a listview |
| **tree_size**    | `"full"`, `"medium"` or `"default"`| `full` - always show full path, `medium` - show folders with the same level on the same indents, `default` - don't show folders with only one child folder. This setting works only with ** tree_view = true ** |
| **group_position**    | `"left"` or `"right"`| Use right or left side for `Opened files` tab. |

## Commands and Keybindings

This plugin add <kbd>ctrl+F1</kbd> keybinding for opening a new tab with `Opened files` but you can change it to your binding.

It also has some key shortcuts for using in `Opened files` tab:

### Shortcuts
| Shortcut         | Command      |
| :--------------- | :----------- |
| <kbd>r</kbd>     | Refresh view |
| <kbd>o</kbd>     | Open selected file with OS default application |
| <kbd>Enter</kbd> | Open selected file or fold/unfold selected directory |
| <kbd>→</kbd>     | Expand directory |
| <kbd>←</kbd>     | Collapse directory |
| <kbd>↑</kbd>     | Go up |
| <kbd>↓</kbd>     | Go down |

### Mouse

You can also use mouse to act with `Opened files` plugin. There is only one action - left double click is the same as <kbd>Enter</kbd> pressing.

## Credits

This plugin uses some code, ideas and color scheme basics from [SublimeFileBrowser plugin](https://github.com/aziz/SublimeFileBrowser) and some functions from [FileHistory plugin](https://github.com/FichteFoll/FileHistory)

### License
This plugin uses MIT license. For more information see the LICENSE file.
