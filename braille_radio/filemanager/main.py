import curses

from braille_radio.base import Screen
from braille_radio.filemanager.intro import FileManagerIntro
from braille_radio.loop import MainLoop


class FileManagerLoop(MainLoop):
    """
    The main instance dispatching keystrokes
    """
    utf8_set = False

    def signal_loop(self):
        self.page.render()
        while True:
            key = self.screen.getkey()
            # handle german Umlauts
            if key == 'Ã':
                self.utf8_set = True
                continue
            if self.utf8_set:
                key = bytes((ord('Ã'), ord(key))).decode()

                self.utf8_set = False
            # handle meta key
            if key == '\x1b':
                # Distinguish between ESC and ALT + key
                # If ESC then the next char is "\1b"
                self.screen.nodelay(True)
                next_key = self.screen.getch()
                self.screen.nodelay(False)
                if next_key == '\x1b' or next_key == -1:
                    # We have the ESC key pressed
                    page = self.page.exit()
                    if page is None:
                        break
                    else:
                        self.page = page
                        self.page.render()
                else:
                    # We have ALT + next_key pressed
                    key = 'ALT+' + chr(next_key)
            if key == '\x04':
                page = self.page.exit()
                if page is None:
                    break
                else:
                    self.page = page
                    self.page.render()
            else:
                res = self.page.notify(key)
                # if res is None the keypress was processed internally and no page change
                # was requested
                if res is not None:
                    # A page change is requested
                    if isinstance(res, Screen):
                        self.page = res
                        self.page.render()
                    # A page change with a callback is requested
                    elif isinstance(res, tuple) and isinstance(res[0], Screen):
                        self.page = res[0]
                        self.page.render()
                        res[1]()


def main():
    gui = FileManagerLoop(FileManagerIntro)
    curses.wrapper(gui)


if __name__ == '__main__':
    main()
