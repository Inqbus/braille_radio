import curses
import os
from _curses import KEY_UP, KEY_LEFT, KEY_F5, KEY_RIGHT, KEY_BACKSPACE
from pathlib import Path
from curses import KEY_ENTER

from braille_radio.base import Screen
from sortedcontainers.sorteddict import SortedDict

from braille_radio.loop import MainLoop


class FileManager(Screen):
    """
    Filemanager Intro Screen
    """

    def init_key_handler(self):
        super(FileManager, self).init_key_handler()
        self.key_handler.f = self.filemanager_start
        self.key_handler.h = self.filemanager_help

    def filemanager_start(self):
        return FileManagerStart(self)

    def filemanager_help(self):
        return FileManagerHelp(self)

    def payload(self):
        self.screen.addstr('Welcome to filemanager! Help is always found on the next line.')
        self.screen.addstr(1, 0, 'Type h for help, f for start')


class FileManagerHelp(Screen):
    """
    Filemanager Intro Screen
    """


class FileManagerStart(Screen):
    """
    Filemanager Intro Screen
    """
    def __init__(self, parent, screen=None):
        super(FileManagerStart, self).__init__(parent, screen=screen)
        # Show dotted files
        self.show_dot = True
        # do search
        self.do_search = False
        # do shift marking
        self.do_mark = False

        self.search_string = None
        self.path = Path(os.getcwd())
        self.current_dir = SortedDict()
        # This initializes the dir_index
        self.depth = len(self.path.parts)
        # This is important to initialize the index on the current folder
        self.dir_index = 0
        self.scan()
        self.old_path = self.path
        self.marked = set()
        # used for marking operation
        self.key_buf = ''

    def init_key_handler(self):
        super(FileManagerStart, self).init_key_handler()
        self.key_handler[KEY_ENTER] = self.dir_down
        self.key_handler['\n'] = self.dir_down
        self.key_handler['KEY_RIGHT'] = self.dir_down
        self.key_handler['KEY_LEFT'] = self.dir_up
        self.key_handler['.'] = self.toggle_dot
        self.key_handler['/'] = self.toggle_search
        self.key_handler['KEY_BACKSPACE'] = self.backspace
        self.key_handler['KEY_F(5)'] = self.mark
        self.key_handler['ALT+b'] = self.mark_begin
        self.key_handler['ALT+e'] = self.mark_end
        self.key_handler['ALT+n'] = self.mark_clear
        self.key_handler['ALT+a'] = self.mark_all
        self.key_handler['ALT+t'] = self.mark_toggle
        self.key_handler['other'] = self.other

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

    def mark_toggle(self):
        self.mark()

    def mark_all(self):
        pass

    def backspace(self):
        if len(self.search_string) > 0:
            self.search_string = self.search_string[:-1]
            self.scan()
            self.render()

    def shift_bracket(self, key):
        pass
        # if self.do_mark:
        #     if self.key_buf == '[':
        #         if key == 'A':
        #             self.()
        #             self.key_buf = ''
        #         elif key == 'B':
        #             self.mark_end()
        #             self.key_buf = ''
        #
        #     if key == '[':
        #         self.key_buf = key

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
        self.render()

    def clear_search(self):
        self.do_search = False
        self.search_string = None

    def dir_down(self):
        self.clear_search()
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

    def dir_up(self):
        self.clear_search()
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

    @property
    def current_dir_entry_path(self):
        return self.path /self.current_dir.items()[self.dir_index][0]

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
        y = 0
        x = 0
        # format the path part
        path_part = f"{'/'.join(self.path.parts[-3:])}"

        # get the file part
        name, payload = self.current_dir_entry

        # Format as directory
        if payload['is_dir']:
            file_part = f'<{name}>'
        else:
            file_part = f'{name}'

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

        self.screen.addstr(1, 0, str(self.dir_index))
        self.screen.addstr(2, 0, str(self.depth))
        self.screen.addstr(3, 0, 'old_path: ' + str(self.old_path))

        self.screen.move(0, len(path_part))

    def cursor_up(self):
        if self.dir_index > 0:
            self.dir_index -= 1
        if self.do_mark:
            self.mark()
        self.render()

    def cursor_down(self):
        if self.dir_index < len(self.current_dir) - 1:
            self.dir_index += 1
        if self.do_mark:
            self.mark()
        self.render()


class FileManagerLoop(MainLoop):
    """
    The main instance dispatching keystrokes
    """

    def signal_loop(self):
        self.page.render()
        while True:
            key = self.screen.getkey()
            # handle meta key
            if key == '\x1b':
                self.meta_set = True
            elif self.meta_set:
                self.meta_set = False
                key = 'ALT+' + key
            if key == '\x04':
                page = self.page.exit()
                if page is None:
                    break
                else:
                    self.page = page
                    self.page.render()
            else:
                res = self.page.notify(key)
                if res is not None:
                    self.page = res
                    self.page.render()
                # else:
                #     print(f'key is {key}')


def main():
    gui = FileManagerLoop(FileManager)
    curses.wrapper(gui)


if __name__ == '__main__':
    main()