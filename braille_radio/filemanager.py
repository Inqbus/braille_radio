import os
from _curses import KEY_UP, KEY_LEFT
from pathlib import Path
from curses import KEY_ENTER

from braille_radio.base import Screen


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
        self.wd = Path(os.getcwd())
        self.depth = len(self.wd.parts)
        self.current_dir = []
        self.current_dir_index = 0
        self.scan()

    def init_key_handler(self):
        super(FileManagerStart, self).init_key_handler()
        self.key_handler[KEY_ENTER] = self.down
        self.key_handler['\n'] = self.down
        self.key_handler['KEY_LEFT'] = self.up
        self.key_handler['.'] = self.toggle_dot

    def toggle_dot(self):
        self.show_dot = not self.show_dot
        self.scan()
        self.render()

    def down(self):
        if self.current_dir[self.current_dir_index][1]:
            self.depth += 1
            self.wd = self.wd / self.current_dir[self.current_dir_index][0]
            self.current_dir_index = 0
            self.scan()
            self.render()

    def up(self):
        self.depth += 1
        old_wd = self.wd
        self.wd = self.wd.parent
        self.scan()
        # find the subdir where we have come from
        self.current_dir_index = self.current_dir.index((old_wd.name, old_wd.is_dir()))
        self.render()

    def scan(self):
        files = []
        for i in self.wd.glob('*'):
            if not self.show_dot and i.name.startswith('.'):
                continue
            files.append((i.name, i.is_dir()))

        files = sorted(files, key=lambda file: (not file[1], file[0].lower()))
        self.current_dir = files
        if len(self.current_dir) == 0:
            self.current_dir = [('|EMPTY|', False)]

    def payload(self):
        left_part = f"{'/'.join(self.wd.parts[-3:])}"
        if self.current_dir[self.current_dir_index][1]:
            middle_part = f'<{self.current_dir[self.current_dir_index][0]}>'
        else:
            middle_part = f'{self.current_dir[self.current_dir_index][0]}'
        self.screen.addstr(left_part + ' ' + middle_part)
        self.screen.move(0, len(left_part))

    def cursor_up(self):
        if self.current_dir_index > 0:
            self.current_dir_index -= 1
        self.render()

    def cursor_down(self):
        if self.current_dir_index < len(self.current_dir) - 1:
            self.current_dir_index += 1
        self.render()
