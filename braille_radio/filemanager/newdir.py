from braille_radio.base import Screen


class NewDir(Screen):
    """
    Filemanager Intro Screen
    """

    def __init__(self, parent, screen=None, x=0, y=0):
        super().__init__(parent, screen=screen)
        self.prompt = "New Dir:"
        self.x = x
        self.y = y
        self.dirname = ''
        self.cursor_pos = 0

    def init_key_handler(self):
        self.key_handler['\n'] = self.create_dir
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

    def insert_char(self, key):
        if len(key) > 1:
            return
        left = self.dirname[:self.cursor_pos]
        right = self.dirname[self.cursor_pos:]
        self.dirname = left + key + right
        self.cursor_right()
        self.render()

    def delete_char(self):
        if len(self.dirname) < self.cursor_pos + 1:
            return
        left = self.dirname[:self.cursor_pos]
        right = self.dirname[self.cursor_pos + 1:]
        self.dirname = left + right
        self.cursor_left()
        self.render()

    def delete_char_left(self):
        left = self.dirname[:self.cursor_pos - 1]
        right = self.dirname[self.cursor_pos:]
        self.dirname = left + right
        self.cursor_left()
        self.render()


    def create_dir(self):
        pass

    def clear_screen(self):
        """
        Clears the screen: We do only clean the current file/dir name but leave the screen intact.
        :return:
        """
        self.screen.move(self.y, self.x)
        self.screen.clrtoeol()

    def payload(self):
        self.screen.addstr(self.y, self.x, self.prompt + self.dirname)
        self.screen.addstr(4, 10, str(self.cursor_pos) + ' ' + str(len(self.dirname)))
        self.screen.move(self.y, self.x + len(self.prompt) + self.cursor_pos)

