import curses

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
                if res is not None:
                    self.page = res
                    self.page.render()
                # else:
                #     print(f'key is {key}')


def main():
    gui = FileManagerLoop(FileManagerIntro)
    curses.wrapper(gui)


if __name__ == '__main__':
    main()