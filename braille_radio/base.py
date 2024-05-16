from addict import Dict


class Screen(object):
    """
    Base class for the GUI.
    Knows its parent for back propagation.
    """
    def __init__(self, parent, screen=None):
        self.parent = parent
        if screen is None and parent is not None:
            self.screen = parent.screen
        else:
            self.screen = screen
        self.key_handler = Dict()
        self.init_key_handler()
        self.init()

    def init_key_handler(self):
        self.key_handler.KEY_UP = self.cursor_up
        self.key_handler.KEY_DOWN = self.cursor_down

    def init(self):
        """
        Initializing the screen
        """
        pass

    def render(self):
        # Clear screen
        self.clear_screen()
        # Bring something on the screen
        self.payload()
        # refresh the screen
        self.screen.refresh()

    def clear_screen(self):
        """
        Clears the screen
        :return:
        """
        self.screen.clear()

    def payload(self):
        """
        Here the real work is done.
        :return:
        """
        pass

    def exit(self):
        return self.parent

    def notify(self, key):
        """
        The notify function is called from the main loop with keycodes to react on.
        :param key:
        :return:
        """
        if key in self.key_handler:
            return self.key_handler[key]()
        elif self.key_handler.other:
            return self.key_handler.other(key)

    def cursor_up(self):
        """
        React on cursor up keystroke
        """
        y, x = self.screen.getyx()
        if y > 0:
            self.screen.move(y - 1, x)
        return True

    def cursor_down(self):
        """
        React on cursor down keystroke
        """
        y, x = self.screen.getyx()
        rows, cols = self.screen.getmaxyx()
        if y < rows - 1:
            self.screen.move(y + 1, x)
        return True
