import re
from curses import wrapper, KEY_ENTER
from braille_radio.radiobrowse import RadioBrowse
import vlc
import os

from braille_radio.rb_index import RadioIndex

# set VLC to verbose for easier debugging
os.environ["VLC_VERBOSE"] = str("-1")

# Bring up an instance of RadioBrowse
rb = RadioBrowse()

# Bring up an instance of RadioIndex
ri = RadioIndex()

# Regex Filter for category keys
CHAR_MAP = re.compile('\w{1}',flags=re.ASCII )


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
        self.init()

    def init(self):
        """
        Initializing the srceen
        """
        pass

    def render(self):
        # Clear screen
        self.screen.clear()
        # Bring something on the screen
        self.payload()
        # refresh the screen
        self.screen.refresh()

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
        The notify function is called from the main loop with with keycodes to react on.
        :param key:
        :return:
        """
        if key == 'KEY_UP':
            self.cursor_up()
            return True
        elif key == 'KEY_DOWN':
            self.cursor_down()
            return True

    def cursor_up(self):
        """
        React on cursor up keystroke
        """
        y, x = self.screen.getyx()
        if y > 0:
            self.screen.move(y - 1, x)

    def cursor_down(self):
        """
        React on cursor down keystroke
        """
        y, x = self.screen.getyx()
        rows, cols = self.screen.getmaxyx()
        if y < rows - 1:
            self.screen.move(y + 1, x)


class Intro(Screen):
    """
    Introductional screen
    """

    def payload(self):
        self.screen.addstr('Welcome to braille radio! Help is always found on the next line.')
        self.screen.addstr(1, 0,
                'Type h for help, r for radio')

    def notify(self, key):
        """
        Show Help and radio option
        """
        super(Intro, self).notify(key)
        if key == 'h':
            return Help(self)
        if key == 'r':
            return Radio(self)


class Help(Screen):
    """
    Help screen shows standard key stroke information
    """

    def payload(self):
        self.screen.addstr('Help')
        self.screen.addstr(1, 0, 'Type ESC to go back')
        self.screen.addstr(2, 0, 'Up/Down moves in lists')

    def render(self):
        # Clear screen
        self.screen.clear()
        self.payload()
        self.screen.refresh()

    def notify(self, key):
        if key == 'q':
            return None
        if key == '':
            return None


class SearchResults(Screen):
    """
    Show the search results of a station search.
    """

    def init(self):
        self.search_results = 'Init!'
        self.search_result_index = 0

    def search(self, search_string):
        self.search_string = search_string
        self.search_results = rb.search(self.search_string)

    def payload(self):
        if len(self.search_results) > 0:
            data = (
                len(self.search_results),
                self.search_string,
                self.search_result_index,
                self.search_results[self.search_result_index]['name']
            )
            self.screen.addstr('%s results for "%s": %s %s' % data )
        else:
            self.screen.addstr('Nothing found for "%s"' % self.search_string)

    def cursor_up(self):
        if self.search_result_index > 0:
            self.search_result_index -= 1
        self.render()

    def cursor_down(self):
        if self.search_result_index < len(self.search_results) - 1:
            self.search_result_index += 1
        self.render()

    def notify(self, key):
        super(SearchResults, self).notify(key)
        if key == 'q':
            return None
        elif key == KEY_ENTER or key == '\n':
            station = StationPlay(self)
            station.tune_to(self.search_results[self.search_result_index])
            return station


class StationPlay(Screen):
    """
    Plays a certain station
    """

    def tune_to(self, station):
        self.station = station

    def payload(self):
        self.screen.addstr(0, 0, 'Playing: %s' % self.station['name'])
        self.p = vlc.MediaPlayer(self.station['url_resolved'])
        self.p.play()

    def exit(self):
        self.p.stop()
        return self.parent

    def notify(self, key):
        pass


class ChannelSearch(Screen):
    """
    Search for a certain channel. Not optimal at the moment!
    """

    def init(self):
        self.search_string = ''
        self.results = []
        self.search_result_index = 0


    def payload(self):
        if len(self.results) > 0:
            self.screen.addstr('Searching: %s : %s %s %s (%s)' % (
                self.search_string,
                len(self.results),
                self.search_result_index + 1,
                self.results[self.search_result_index]['name'],
                self.results[self.search_result_index]['tags'],
            )
            )
        else:
            self.screen.addstr('Searching: %s : No results : TYPE TO SEARCH!' % (
                self.search_string,
                )
            )

    def notify(self, key):
        if super(ChannelSearch, self).notify(key):
            return
        if key == 'ESC':
            return self.parent
        elif key == 'KEY_BACKSPACE':
            if len(self.search_string) > 0:
                self.search_string = self.search_string[:-1]
                self.results = ri.search(self.search_string)
                self.search_result_index = 0
                self.render()
        elif key == KEY_ENTER or key == '\n':
            station = StationPlay(self)
            station.tune_to(self.results[self.search_result_index])
            return station
        else :
            self.search_string += key
            self.results = ri.search(self.search_string)
            self.search_result_index = 0
            self.render()

    def cursor_up(self):
        if self.search_result_index > 0:
            self.search_result_index -= 1
        self.render()

    def cursor_down(self):
        if self.search_result_index < len(self.results) - 1:
            self.search_result_index += 1
        self.render()


class CategoryResults(SearchResults):
    """
    Shown category results
    """

    def search(self, search_string):
        self.search_string = search_string
        self.search_results = rb.search_category(self.search_string)



class Categories(Screen):
    """
    Navigate category results
    """

    def init(self):
        self.categories = rb.categories()
        self.category_index = 0

    def jump(self, key):
        for idx, category in enumerate(self.categories):
            if category['name'][0] == key:
                break
        if idx < len(self.categories):
            self.category_index = idx
            self.render()

    def payload(self):
        self.screen.addstr('Categories')

        self.screen.addstr(1, 0, '%s Categories: %s %s (%s)' %
                                 (
                        len(self.categories),
                        self.category_index + 1,
                        self.categories[self.category_index]['name'],
                        self.categories[self.category_index]['stationcount'],
                                 )
                            )
        self.screen.move(1,0)

    def notify(self, key):
        super(Categories, self).notify(key)
        if key == KEY_ENTER or key == '\n':
            result = CategoryResults(self)
            result.search(self.categories[self.category_index]['name'])
            return result
        else :
            if len(key)== 1 and CHAR_MAP.match(key):
                self.jump(key)


    def cursor_up(self):
        if self.category_index > 0:
            self.category_index -= 1
        self.render()

    def cursor_down(self):
        if self.category_index < len(self.categories) - 1:
            self.category_index += 1
        self.render()


class Update(Screen):
    """
    Update and reindex the station information
    """

    def payload(self):
        self.screen.addstr('Update station index? Please type y to confirm. ')

    def notify(self, key):
        super(Update, self).notify(key)
        if key == 'y':
            return Updated(self)


class Updated(Screen):
    """
    Do the updating and return to the radio view.
    """

    def payload(self):
        self.screen.addstr('Updating station index. Please wait. ')
        ri.index_stations()
        self.screen.addstr('Station index updated.')
        main.page = self.parent.parent
        main.page.render()


class Radio(Screen):
    """
    Top level view for the radio.
    """

    def payload(self):
        self.screen.addstr('Radio')
        self.screen.addstr(2, 0, 'Type s to search for stations')
        self.screen.addstr(1, 0, 'Type c für categories')
        self.screen.addstr(3, 0, 'Up/down selects station')
        self.screen.addstr(4, 0, 'Hit enter to play station')
        self.screen.addstr(5, 0, 'Type u to update station index (needs some time!)')
        self.screen.move(0,0)

    def notify(self, key):
        super(Radio, self).notify(key)
        if key == 's':
            return ChannelSearch(self, self.screen)
        elif key == 'c':
            return Categories(self, self.screen)
        elif key == 'u':
            return Update(self, self.screen)



class Main(object):
    """
    The main instance dispatching keystrokes
    """

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


main = Main(Intro)
wrapper(main)
