from os.path import expanduser, join, exists
from os import makedirs


home = expanduser("~")

base = join(home,'.cache','braille_radio')

if not exists(base):
    makedirs(base)


STATION_INDEX_DIR = join(base, "station_index")

FAVORITES_INDEX_DIR = join(base, "favorite_index")

