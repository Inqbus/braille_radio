import os
from _curses import KEY_UP, KEY_LEFT
from pathlib import Path
from curses import KEY_ENTER

from braille_radio.base import Screen
from sortedcontainers.sorteddict import SortedDict


class FileManager(Screen):
    """
    Filemanager Intro Screen
    """

    def init_key_handler(self):
        super(FileManager, self).init_key_handler()
        self.key_handler.f = self.filemanager_start

    def filemanager_start(self):
        return FileManagerStart(self)

    def payload(self):
        self.screen.addstr('Welcome to filemanager! Help is always found on the next line.')
        self.screen.addstr(1, 0, 'Type h for help, f for start')


class FileManagerStart(Screen):
    """
    Filemanager Intro Screen
    """
    def __init__(self, parent, screen=None):
        super(FileManagerStart, self).__init__(parent, screen=screen)
        self.show_dot = True
        self.do_search = False
        self.search_string = None
        self.path = Path(os.getcwd())
        self.current_dir = SortedDict()
        # This initializes the dir_index
        self.depth = len(self.path.parts)
        # This is important to initialize the index on the current folder
        self.dir_index = 0
        self.scan()
        self.old_path = self.path

    def init_key_handler(self):
        super(FileManagerStart, self).init_key_handler()
        self.key_handler[KEY_ENTER] = self.down
        self.key_handler['\n'] = self.down
        self.key_handler['KEY_RIGHT'] = self.down
        self.key_handler['KEY_LEFT'] = self.up
        self.key_handler['.'] = self.toggle_dot
        self.key_handler['/'] = self.search
        self.key_handler['KEY_BACKSPACE'] = self.backspace
        self.key_handler['other'] = self.other

    def backspace(self):
        if len(self.search_string) > 0:
            self.search_string = self.search_string[:-1]
            self.scan()
            self.render()

    def other(self, key):
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

    def search(self):
        self.do_search = not self.do_search
        if not self.do_search:
            self.search_string = None
        self.scan()
        self.render()

    def down(self):
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
                    self.dir_index = self.current_dir.index(old_entry)
                except ValueError:
                    # the old path part is not found.
                    self.dir_index = 0
                    self.old_path = self.path

            self.render()

    def up(self):
        came_from = self.current_dir.items()[self.dir_index][0]
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
            self.dir_index = self.current_dir.index(old_wd.parts[self.depth])
        except ValueError:
            # Dir entry does not exist anymore
            self.dir_index = 0
        self.render()

    @property
    def current_dir_entry(self):
        return self.current_dir.items()[self.dir_index]

    def scan(self):

        self.current_dir = SortedDict()

        for i in self.path.glob('*'):
            if not self.show_dot and i.name.startswith('.'):
                continue
            if self.search_string is not None and self.search_string not in i.name:
                continue
            file_ds = {'is_dir': i.is_dir()}
            self.current_dir[i.name] = file_ds

    def payload(self):
        left_part = f"{'/'.join(self.path.parts[-3:])}"
        name, payload = self.current_dir_entry
        if payload['is_dir']:
            middle_part = f'<{name}>'
        else:
            middle_part = f'{name}'
        if self.do_search:
            if self.search_string:
                self.screen.addstr(left_part + ' Filter:' + self.search_string + ' ' + middle_part)
            else:
                self.screen.addstr(left_part + ' Filter:<all> ' + middle_part)
        else:
            self.screen.addstr(left_part + ' ' + middle_part)

        self.screen.addstr(1, 0, str(self.dir_index))
        self.screen.addstr(2, 0, str(self.depth))
        self.screen.addstr(3, 0, 'old_path: ' + str(self.old_path))

        self.screen.move(0, len(left_part))

    def cursor_up(self):
        if self.dir_index > 0:
            self.dir_index -= 1
        self.render()

    def cursor_down(self):
        if self.dir_index < len(self.current_dir) - 1:
            self.dir_index += 1
        self.render()
