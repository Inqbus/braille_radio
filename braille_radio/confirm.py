from _curses import KEY_ENTER

from braille_radio.base import Screen

POPUP_LINE = 4


class PopUp(Screen):

    def __init__(self, parent, msg=None, screen=None):
        super().__init__(parent, screen=screen)
        self.msg = msg

    def payload(self):
        self.screen.addstr(POPUP_LINE, 0, self.msg + ' Press enter to return')
        self.screen.move(POPUP_LINE, 0)

    def clear_screen(self):
        """
        Clear screen does nothing. Popup does not disturb.
        :return:
        """
        self.screen.move(POPUP_LINE, 0)
        self.screen.clrtoeol()

    def init_key_handler(self):
        super().init_key_handler()
        self.key_handler[KEY_ENTER] = self.leave
        self.key_handler['\n'] = self.leave

    def leave(self):
        self.clear_screen()
        return self.parent


class Choice(Screen):

    def __init__(self, parent, msg=None, screen=None, yes=None, no=None):
        super().__init__(parent, screen=screen)
        self.msg = msg
        self.yes = yes
        self.no = no

    def init_key_handler(self):
        super().init_key_handler()
        self.key_handler[KEY_ENTER] = self.yes
        self.key_handler['\n'] = self.yes
        self.key_handler['other'] = self.no

    def no(self):
        self.clear_screen()
        if self.no is not None:
            return self.parent, self.no
        else:
            return self.parent

    def yes(self):
        self.clear_screen()
        if self.yes is not None:
            return self.parent, self.yes
        else:
            return self.parent


    def payload(self):
        self.screen.addstr(POPUP_LINE, 0, self.msg + ' Press [n]/y')
        self.screen.move(POPUP_LINE, 0)

