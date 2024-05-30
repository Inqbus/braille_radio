import shutil

from braille_radio.confirm import PopUp, Choice
from braille_radio.filemanager.base import FileManagerScreen
from braille_radio.filemanager.view import FileManager


class FileManagerMain(FileManagerScreen):
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
        return self.view

    @property
    def view(self):
        return self.views[self.view_idx]

    @property
    def other_view(self):
        return self.views[1 - self.view_idx]

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

    def copy_confirm(self):
        if self.view.path == self.other_view.path:
            return PopUp(self.view, msg='Source and Target are identical!')
        else:
            return Choice(self.view, msg='Copy: Are you sure?', yes=self.copy)

    def move_confirm(self):
        if self.view.path == self.other_view.path:
            return PopUp(self.view, msg='Source and Target are identical!')
        else:
            return Choice(self.view, msg='Move: Are you sure?', yes=self.move)

    def delete_confirm(self):
        return Choice(self.view, msg='Delete: Are you sure?', yes=self.delete)

    def copy(self):
        for item in self.view.marked:
            if item.is_dir():
                shutil.copytree(item, self.other_view.path)
            else:
                shutil.copy2(item, self.other_view.path)
        self.other_view.scan()
        self.other_view.render()
        self.view.render()

    def move(self):
        for item in self.view.marked:
            shutil.move(item, self.other_view.path)
        self.view.marked = set()
        self.view.scan()
        self.other_view.scan()
        self.view.render()
        self.other_view.render()
        return self.view

    def delete(self):
        for item in self.view.marked:
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
        self.view.marked = set()

        self.view.scan()
        self.view.render()

