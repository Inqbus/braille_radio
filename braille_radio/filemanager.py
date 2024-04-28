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
        self.wd = Path(os.getcwd())
        self.depth = len(self.wd.parts)
        self.local = []
        self.local_index = 0
        self.scan()

    def init_key_handler(self):
        super(FileManagerStart, self).init_key_handler()
        self.key_handler[KEY_ENTER] = self.down
        self.key_handler['\n'] = self.down
        self.key_handler['KEY_LEFT'] = self.up

    def down(self):
        if self.local[self.local_index][1]:
            self.depth += 1
            self.wd = self.wd / self.local[self.local_index][0]
            self.scan()
            self.render()

    def up(self):
        self.depth += 1
        self.wd = self.wd.parent
        self.scan()
        self.render()

    def scan(self):
        self.local = []
        for i in os.scandir(self.wd):
            self.local.append((f'{i.name}', i.is_dir()))

        self.local_index = 0

    def payload(self):
        if self.local[self.local_index][1]:
            self.screen.addstr(f'{self.wd} <{self.local[self.local_index][0]}>')
        else:
            self.screen.addstr(f'{self.wd} {self.local[self.local_index][0]}')

    def cursor_up(self):
        if self.local_index > 0:
            self.local_index -= 1
        self.render()

    def cursor_down(self):
        if self.local_index < len(self.local) - 1:
            self.local_index += 1
        self.render()