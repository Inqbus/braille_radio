from braille_radio.base import Screen
from braille_radio.filemanager.view import FileManager


class FileManagerMain(Screen):
    """
    Filemanager Screen
    """

    views = None
    view_idx = 0

    def init(self):
        """
        Initializing the screen
        """
        self.views = [
            FileManager(parent=self, display_line=0),
            FileManager(parent=self, display_line=1),
            ]

    @property
    def view(self):
        return self.views[self.view_idx]

    def toggle_view(self):
        self.view_idx = 1 - self.view_idx
        return self.view

    def payload(self):
        self.views[1].payload()
        self.views[0].payload()

    def init_key_handler(self):
        super(FileManagerMain, self).init_key_handler()
        self.key_handler['\t'] = self.toggle_view
        self.key_handler['other'] = self.dispatch_key

    def dispatch_key(self, key):
        self.view.notify(key)
