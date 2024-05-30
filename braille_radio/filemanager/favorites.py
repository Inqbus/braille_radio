import curses
import shelve
from pathlib import Path

from braille_radio.config import DIR_FAVORITES
from braille_radio.filemanager.base import FileManagerScreen


class FileManagerFavorites(FileManagerScreen):

    def __init__(self, parent):
        super().__init__(parent)
        self.display_line = self.parent.display_line
        self.current_favorite = None
        self.sorted_favorites = None
        self.favorites_store = shelve.open(DIR_FAVORITES)
        self.update_favorites()
        self.init()

    def update_favorites(self, favorite=None):
        self.sorted_favorites = sorted(self.favorites_store)
        if favorite is None:
            if len(self.favorites_store) != 0:
                self.current_favorite = 0
        else:
            self.current_favorite = self.sorted_favorites.index(favorite)

    def add(self, favorite):
        self.favorites_store[favorite] = 0
        self.update_favorites()

    def clear_screen(self):
        self.screen.move(self.display_line, 0)
        self.screen.clrtoeol()

    def payload(self):
        if self.current_favorite is None:
            return
        self.screen.addstr(self.display_line, 0, self.sorted_favorites[self.current_favorite], curses.A_REVERSE)

    def cursor_up(self):
        if self.current_favorite > 0:
            self.current_favorite -= 1
        self.render()

    def cursor_down(self):
        if self.current_favorite < len(self.sorted_favorites) - 1:
            self.current_favorite += 1
        self.render()