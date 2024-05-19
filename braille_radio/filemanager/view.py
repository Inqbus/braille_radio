import curses
import os
from pathlib import Path
from curses import KEY_ENTER

from braille_radio.base import Screen
from sortedcontainers.sorteddict import SortedDict


class FileManager(Screen):
    """
    Filemanager Intro Screen
    """
    def __init__(self, parent, screen=None, display_line=0):
        super(FileManager, self).__init__(parent, screen=screen)
        # where to show myself
        self.display_line = display_line
        # Show dotted files
        self.show_dot = True
        # do search
        self.do_search = False
        # do shift marking
        self.do_mark = False
        # Number of path parts shown
        self.number_of_path_parts = 3
        # The type ahead ssearch string
        self.search_string = None
        # the actual file system path
        self.path = Path(os.getcwd())
        # The files in the current_dir
        self.current_dir_files = SortedDict()
        # This initializes the dir_index
        self.depth = len(self.path.parts)
        # This is important to initialize the index on the current folder
        self.dir_index = 0
        # Initial Scan of the current directory
        self.scan()
        # Initialize old_path for memorizing the path history
        self.old_path = self.path
        # The files marked in the current directory marked
        self.marked = set()

    def init_key_handler(self):
        super(FileManager, self).init_key_handler()
        self.key_handler['\t'] = self.parent.toggle_view
        self.key_handler[KEY_ENTER] = self.dir_down
        self.key_handler['\n'] = self.dir_down
        self.key_handler['KEY_RIGHT'] = self.dir_down
        self.key_handler['KEY_LEFT'] = self.dir_up
        self.key_handler['.'] = self.toggle_dot
        self.key_handler['/'] = self.toggle_search
        self.key_handler['KEY_BACKSPACE'] = self.backspace
        self.key_handler['ALT+a'] = self.mark_all
        self.key_handler['ALT+b'] = self.mark_begin
        self.key_handler['ALT+c'] = self.parent.copy_confirm
        self.key_handler['ALT+d'] = self.parent.delete_confirm
        self.key_handler['ALT+e'] = self.mark_end
        self.key_handler['ALT+m'] = self.parent.move_confirm
        self.key_handler['ALT+n'] = self.mark_clear
        self.key_handler['ALT+t'] = self.mark_toggle
        self.key_handler['ALT+È'] = self.increase_depth
        self.key_handler['ALT+-'] = self.decrease_depth
        self.key_handler['other'] = self.other

    def increase_depth(self):
        self.number_of_path_parts += 1
        self.render()

    def decrease_depth(self):
        if self.number_of_path_parts > 2:
            self.number_of_path_parts -= 1
            self.render()

    def mark(self):
        file_path = self.current_dir_entry_path
        if file_path in self.marked:
            self.marked.remove(file_path)
        else:
            self.marked.add(file_path)
        self.render()

    def mark_begin(self):
        self.do_mark = True
        self.mark()

    def mark_end(self):
        self.do_mark = False

    def mark_clear(self):
        self.marked = set()
        self.do_mark = False
        self.render()

    def mark_toggle(self):
        self.mark()

    def mark_all(self):
        for path in self.current_dir_files.items():
            self.marked.add(self.path / path[0])
        self.render()

    def backspace(self):
        if len(self.search_string) > 0:
            self.search_string = self.search_string[:-1]
            self.scan()
            self.render()

    def toggle_view(self, key):
        pass

    def other(self, key):
        if self.do_search:
            self.append_to_filter(key)

    def append_to_filter(self, key):
        if self.search_string:
            self.search_string += key
        else:
            self.search_string = key

        self.scan()
        self.dir_index = 0
        self.render()

    def toggle_dot(self):
        self.show_dot = not self.show_dot
        self.scan()
        self.render()

    def toggle_search(self):
        self.do_search = not self.do_search
        if not self.do_search:
            self.search_string = None
            self.scan()
        self.render()

    def clear_search(self):
        self.do_search = False
        self.search_string = None

    def dir_down(self):
        self.clear_search()
        # We cannot go into an empty directory
        if self.current_dir_entry[1] is None:
            return
        # We can only go into a directory
        if self.current_dir_entry[1]['is_dir']:
            new_dir = self.current_dir_entry[0]
            self.path = self.path / new_dir

            # check if we have been here already?
            # if yes
            if len(self.old_path.parts) > self.depth + 1:
                # check if the dir we are moving to is on the old_path ..
                if self.old_path.parts[self.depth] == new_dir:
                    old_entry = self.old_path.parts[self.depth + 1]
                else:
                    # else we have to cut the old_path here
                    self.old_path = self.path
                    old_entry = None
            else:
                # if not, then the current path has to set as old_path.
                self.old_path = self.path
                old_entry = None

            self.depth += 1

            self.scan()

            # Find the old_entry for the current directory. It may be renamed, deleted though.
            # If not found set it to zero
            if old_entry is None:
                self.dir_index = 0
            else:
                try:
                    self.dir_index = self.current_dir_files.index(old_entry)
                except ValueError:
                    # the old path part is not found.
                    self.dir_index = 0
                    self.old_path = self.path

            self.render()

    def dir_up(self):
        # in Depth the "/" is counted, so we have to bail out at 1
        if self.depth == 1:
            return
        self.clear_search()
        if self.current_dir_files:
            came_from = self.current_dir_files.items()[self.dir_index][0]
            # check if we go up along the route of the old_path
            if len(self.old_path.parts) > self.depth:
                if self.old_path.parts[self.depth] != came_from:
                    # if we go up from another route the current old_path is invalid
                    self.old_path = self.path / came_from

            else:
                # We have not previously been here so memoize the location
                self.old_path = self.old_path / came_from

        self.depth -= 1

        # check if the dir entry upward is stil there (could be deleted though)
        old_wd = self.path
        self.path = self.path.parent
        self.scan()
        try:
            self.dir_index = self.current_dir_files.index(old_wd.parts[self.depth])
        except ValueError:
            # Dir entry does not exist anymore
            self.dir_index = 0
        self.render()

    @property
    def current_dir_entry(self):
        if self.current_dir_files:
            return self.current_dir_files.items()[self.dir_index]
        else:
            return (None, None)

    @property
    def current_dir_entry_path(self):
        if self.current_dir_files:
            return self.path /self.current_dir_files.items()[self.dir_index][0]

    def scan(self):

        self.current_dir_files = SortedDict()

        for i in self.path.glob('*'):
            if not self.show_dot and i.name.startswith('.'):
                continue
            if self.search_string is not None and self.search_string not in i.name:
                continue
            file_ds = {'is_dir': i.is_dir()}
            self.current_dir_files[i.name] = file_ds

    def clear_screen(self):
        """
        Clears the screen
        :return:
        """
        self.screen.move(self.display_line, 0)
        self.screen.clrtoeol()

    def payload(self):
        y = self.display_line
        x = 0
        # format the path part
        path_part_wihout_root = self.path.parts[1:]
        path_part = f"/{'/'.join(path_part_wihout_root[-self.number_of_path_parts:])}"

        # get the file part
        name, payload = self.current_dir_entry

        if payload is not None:
            # Format as directory
            if payload['is_dir']:
                file_part = f'<{name}>'
            else:
                file_part = f'{name}'
        else:
            file_part = f'!empty!'

        # Set display attributes on file_part
        file_part_format = curses.A_NORMAL

        if self.current_dir_entry_path in self.marked:
            file_part_format |= curses.A_REVERSE

        # Handle the display of searching
        if self.do_search:
            if self.search_string:
                filter_part = ' Filter:' + self.search_string + ' '
            else:
                filter_part = ' Filter:<all> '
        else:
            filter_part = ' '

        self.screen.addstr(y, x, path_part)
        x += len(path_part)
        self.screen.addstr(y, x, filter_part)
        x += len(filter_part)
        self.screen.addstr(y, x, file_part, file_part_format)

        self.screen.move(y, len(path_part))

    def cursor_up(self):
        if self.dir_index > 0:
            self.dir_index -= 1
        if self.do_mark:
            self.mark()
        self.render()

    def cursor_down(self):
        if self.dir_index < len(self.current_dir_files) - 1:
            self.dir_index += 1
        if self.do_mark:
            self.mark()
        self.render()


