import _curses

from braille_radio.base import Screen


class FileManagerHelp(Screen):
    """
    Help screen shows standard keystroke information
    """

    def __init__(self, parent, screen=None, current_screen_line=None):
        super().__init__(parent, screen=screen)
        if current_screen_line is not None:
            self.current_screen_line = current_screen_line
        else:
            self.current_screen_line = 0

    def init_key_handler(self):
        self.key_handler['ALT+q'] = self.go_back

    def go_back(self):
        return self.parent

    def payload(self):
        self.current_line = 3
        self.append_line('Help')
        self.append_line('Navigation:  ALT+q -> exit view; TAB changes between source and target line')
        self.append_line('Cursor Up/Down moves in lists; Left/Right go directory up/down')
        self.append_line('Visual: ALT++/ALT+- increase or decrease the number of path elements shown')
        self.append_line('ALT+. toggle display of dot-files')
        self.append_line('Filter: ALT+/ Toggle filter mode')
        self.append_line('Selection:  ALT+t toggles mark on the current file/directory')
        self.append_line('ALT+a marks all entries in a directory; ALT+x unset all marks')
        self.append_line('ALT+b set start of marking; ALT+e set end of marking')
        self.append_line('Operations: ALT+c Copy, ALT+d Delete, ALT+m Move , ALT+n New, ALT+r Rename')

    def clear_screen(self):
        """
        Clears the screen
        :return:
        """
        pass

    def append_line(self, line):
        try:
            self.screen.addstr(self.current_screen_line, 0, line)
        except _curses.error:
            return
        self.screen.move(self.current_screen_line, len(line))
        self.screen.clrtoeol()
        self.current_screen_line += 1

    def render(self):
        # Clear screen
        self.clear_screen()
        self.payload()
        self.screen.refresh()