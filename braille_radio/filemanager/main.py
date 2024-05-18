import curses

from braille_radio.base import Screen
from braille_radio.filemanager.intro import FileManagerIntro
from braille_radio.loop import MainLoop


class FileManagerLoop(MainLoop):
    """
    The main instance dispatching keystrokes
    """

    def signal_loop(self):
        self.page.render()
        while True:
            key = self.screen.getkey()
            # handle meta key
            if key == '\x1b':
                self.meta_set = True
                continue
            elif self.meta_set:
                self.meta_set = False
                key = 'ALT+' + key
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
