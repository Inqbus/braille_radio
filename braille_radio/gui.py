import re
from curses import KEY_ENTER, KEY_CTAB, KEY_BACKSPACE

import vlc
import os

from curses import wrapper

from addict import Dict

from braille_radio.indexing import StationIndex
from braille_radio.indexing import FavoriteIndex


# Bring up an instance of radio brwose index
station_index = StationIndex()

# Bring up an instance of Favorites
favorite_index = FavoriteIndex()

# set VLC to verbose for easier debugging
os.environ["VLC_VERBOSE"] = str("-1")

# Regex Filter for category keys
CHAR_MAP = re.compile('\w{1}',flags=re.ASCII )

ALL_STATIONS = list(station_index.ix.searcher().documents())



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
        if key in self.key_handler :
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


class Intro(Screen):
    """
    Introductional screen
    """
    def init_key_handler(self):
        super(Intro, self).init_key_handler()
        self.key_handler.h = self.help
        self.key_handler.r = self.radio

    def help(self):
        return Help(self)

    def radio(self):
        return Radio(self)

    def payload(self):
        self.screen.addstr('Welcome to braille radio! Help is always found on the next line.')
        self.screen.addstr(1, 0,
                'Type h for help, r for radio')


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


class AddFavorite(Screen):
    """
    Plays a certain station
    """

    def __init__(self, parent, index, screen=None):
        super(AddFavorite, self).__init__(parent,screen=screen)
        self.index = index

    def mark(self, station):
        self.station = station
        self.index.mark(station)

    def payload(self):
        self.screen.addstr(0, 0, 'Added: %s to favorites' % self.station['name'])

    def exit(self):
        return self.parent

    def notify(self, key):
        pass


class StationSearch(Screen):
    """
    Search for a certain station.
    """
    def __init__(self, parent, index, screen=None):
        self.index = index
        super(StationSearch, self).__init__(parent,screen=screen)

    def init(self):
        self.search_string = False
        self.results = ALL_STATIONS
        self.search_result_index = 0

    def payload(self):
        if len(self.results) > 0:
            if not self.search_string:
                _search_string = '<all>'
            else:
                _search_string = self.search_string
            self.screen.addstr('Filter:%s Stations %s : %s %s (%s)' % (
                _search_string,
                len(self.results),
                self.search_result_index + 1,
                self.results[self.search_result_index]['name'],
                self.results[self.search_result_index]['tags'],
            )
            )
        else:
            self.screen.addstr('Filter:%s : No results : TYPE TO SEARCH!' % (
                self.search_string,
                )
            )
        self.screen.addstr(1, 0, 'Up/Down moves in results')
        self.screen.addstr(2, 0, 'Hit enter to play selected station')
        self.screen.addstr(3, 0, 'Hit TAB to mark station as favorite')
        self.screen.move(0,0)

    def init_key_handler(self):
        super(StationSearch, self).init_key_handler()
        self.key_handler['KEY_BACKSPACE'] = self.backspace
        self.key_handler[KEY_ENTER] = self.enter
        self.key_handler['\n'] = self.enter
        self.key_handler[KEY_CTAB] = self.tab
        self.key_handler['\t'] = self.tab
        self.key_handler['other'] = self.other

    def backspace(self):
        if len(self.search_string) > 0:
            self.search_string = self.search_string[:-1]
            self.results = self.index.search(self.search_string)
            self.search_result_index = 0
            self.render()

    def enter(self):
        station = StationPlay(self)
        station.tune_to(self.results[self.search_result_index])
        return station

    def tab(self):
        if self.results:
            favorite = AddFavorite(self, favorite_index)
            favorite.mark(self.results[self.search_result_index])
            return favorite

    def other(self, key):
        if self.search_string:
            self.search_string += key
        else:
            self.search_string = key
        self.results = self.index.search(self.search_string)
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


class FavoriteSearch(StationSearch):

    def init(self):
        self.search_string = ''
        self.results = list(self.index.ix.searcher().documents())
        self.search_result_index = 0



class CategoryResults(StationSearch):
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

    def init_key_handler(self):
        super(Update, self).init_key_handler()
        self.key_handler.y = self.update

    def update(self):
        return Updated(self, station_index )

    def payload(self):
        self.screen.addstr('Update station index? Please type y to confirm or ESC to go back. ')



class Updated(Screen):
    """
    Do the updating and return to the radio view.
    """
    def __init__(self, parent, index, screen=None):
        self.index = index
        super(Updated, self).__init__(parent,screen=screen)

    def payload(self):
        self.screen.addstr('Updating station index. Please wait. ')
        self.index.init()
        self.screen.addstr('Station index updated.')
        main.page = self.parent.parent
        main.page.render()


class Radio(Screen):
    """
    Top level view for the radio.
    """

    def init_key_handler(self):
        super(Radio, self).init_key_handler()
        self.key_handler.s = self.station_search
        self.key_handler.f = self.favorite_search
 #       self.key_handler.c = self.categories()
        self.key_handler.u = self.update_stations

    def station_search(self):
        return StationSearch(self, station_index, self.screen)

    def favorite_search(self):
        return FavoriteSearch(self, favorite_index, self.screen)

#    def categories(self):
#        return Categories(self, self.screen)

    def update_stations(self):
       return Update(self, self.screen)

    def payload(self):
        self.screen.addstr('Radio')
        self.screen.addstr(1, 0, 'Type s to search for stations')
        self.screen.addstr(2, 0, 'Type f for your favorites')
#        self.screen.addstr(3, 0, 'Type c for categories search')
        self.screen.addstr(3, 0, 'Type u to update station index (needs some time!)')
        self.screen.move(0,0)



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


def main():
    gui = Main(Intro)
    wrapper(gui)


if __name__ == '__main__':
    main()
