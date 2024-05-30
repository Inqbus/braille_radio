from braille_radio.base import Screen


class FileManagerScreen(Screen):

    def init_key_handler(self):
        super().init_key_handler()
        self.key_handler['ALT+q'] = self.exit
