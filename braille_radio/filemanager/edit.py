import os
import re

from braille_radio.base import Screen


VALID_CHARS = re.compile("[a-zA-Z0-9-_' .äöüÄÜÖ]")


class Edit(Screen):
    """
    Edit a file or directory name
    """

    def __init__(self, parent, path, x, y, screen=None):
        super().__init__(parent, screen=screen)
        self.path = path
        self.name = ''
        self.x = x
        self.y = y

        self.prompt = "New Dir:"
        self.cursor_pos = 0

    def init_key_handler(self):
        self.key_handler['\n'] = self.update
        self.key_handler['KEY_RIGHT'] = self.cursor_right
        self.key_handler['KEY_LEFT'] = self.cursor_left
        self.key_handler['KEY_BACKSPACE'] = self.delete_char_left
        self.key_handler['KEY_DC'] = self.delete_char
        self.key_handler['other'] = self.insert_char

    def cursor_left(self):
        if self.cursor_pos > 0:
            self.cursor_pos -= 1
            self.render()

    def cursor_right(self):
        if self.cursor_pos < 80:
            self.cursor_pos += 1
            self.render()

    def valid_char(self, char):
        return VALID_CHARS.match(char)

    def insert_char(self, key):
        if len(key) > 1:
            return
        if not self.valid_char(key):
            return
        left = self.name[:self.cursor_pos]
        right = self.name[self.cursor_pos:]
        self.name = left + key + right
        self.cursor_right()
        self.render()

    def delete_char(self):
        if len(self.name) < self.cursor_pos + 1:
            return
        left = self.name[:self.cursor_pos]
        right = self.name[self.cursor_pos + 1:]
        self.name = left + right
        self.cursor_left()
        self.render()

    def delete_char_left(self):
        left = self.name[:self.cursor_pos - 1]
        right = self.name[self.cursor_pos:]
        self.name = left + right
        self.cursor_left()
        self.render()

    def update(self):
        pass

    def clear_screen(self):
        """
        Clears the screen: We do only clean the current file/dir name but leave the screen intact.
        :return:
        """
        self.screen.move(self.y, self.x)
        self.screen.clrtoeol()

    def payload(self):
        self.screen.addstr(self.y, self.x, self.prompt + self.name)
        self.screen.addstr(4, 10, str(self.cursor_pos) + ' ' + str(len(self.name)))
        self.screen.move(self.y, self.x + len(self.prompt) + self.cursor_pos)


class NewDir(Edit):

    def update(self):
        return self.parent.do_new_dir(self.name)


class Rename(Edit):

    def __init__(self, parent, entity, x, y, screen=None):
        super().__init__(parent, entity[0], x, y, screen=screen)
        self.entity = entity
        self.name = entity[0]

    def update(self):
        return self.parent.do_rename(self.entity, self.name)
