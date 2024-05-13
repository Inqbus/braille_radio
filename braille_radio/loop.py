
class MainLoop(object):
    """
    The main instance dispatching keystrokes
    """
    page = None
    meta_set = None

    def __init__(self, initial_page_class):
        self.initial_page_class = initial_page_class

    def __call__(self, screen):
        self.screen = screen
        self.run()

    def run(self):
        self.page = self.initial_page_class(None, self.screen)
        self.signal_loop()

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
            if key == '':
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
