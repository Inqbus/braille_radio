import sys

from braille_radio.filemanager.base import FileManagerScreen
from braille_radio.filemanager.filemanager import FileManagerMain
from braille_radio.filemanager.help import FileManagerHelp


class FileManagerIntro(FileManagerScreen):
    """
    Filemanager Intro Screen
    """

    def init_key_handler(self):
        super(FileManagerIntro, self).init_key_handler()
        self.key_handler.f = self.filemanager_start
        self.key_handler.h = self.filemanager_help
        self.key_handler['ALT+q'] = self.go_back

    def go_back(self):
        sys.exit(0)

    def filemanager_start(self):
        # We must return the view here, to direct the keys to the view.
        fm = FileManagerMain(self)
        fm.render()
        return fm.view

    def filemanager_help(self):
        return FileManagerHelp(self)

    def payload(self):
        self.screen.addstr('Welcome to filemanager! Help is always found on the next line.')
        self.screen.addstr(1, 0, 'Type h for help, f for start')
