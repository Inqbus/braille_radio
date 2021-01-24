import os, os.path
from whoosh import index
from whoosh.fields import Schema, NGRAM, ID

from braille_radio.config import FAVORITES_INDEX_DIR, STATION_INDEX_DIR
from braille_radio.radiobrowse import RadioBrowse
from whoosh.qparser import MultifieldParser

import progressbar

SCHEMA = Schema(
        name=NGRAM(stored=True),
        tags=NGRAM(stored=True),
        url_resolved=ID(stored=True)
)


class Index(object):
    index_dir = None

    def __init__(self):

        if not os.path.exists(self.index_dir):
            os.mkdir(self.index_dir)

        if index.exists_in(self.index_dir):
            self.ix = index.open_dir(self.index_dir)
        else:
            self.ix = index.create_in(self.index_dir, SCHEMA)
            self.init()

    def init(self):
        pass

    def search(self, term):
        qp = MultifieldParser(['name','tags'], schema=SCHEMA)
        q = qp.parse(term)

        searcher = self.ix.searcher()
        results = searcher.search(q, limit=None)
        return results


class FavoriteIndex(Index):
    index_dir = FAVORITES_INDEX_DIR

    def mark(self, station):
        self.writer = self.ix.writer()
        self.writer.add_document(
                    name=station['name'],
                    tags=station['tags'],
                    url_resolved=station['url_resolved'],
            )
        self.writer.commit()

    def unmark(self, station):
        self.writer = self.ix.writer()
        self.writer.delete_document( station['url_resolved'] )
        self.writer.commit()


class StationIndex(Index):
    index_dir = STATION_INDEX_DIR

    def init(self):
        print('Indexing all available stations. This can take a minute or two.')
        rb = RadioBrowse()
        all_stations = rb.all_stations()

        self.writer = self.ix.writer(procs=4, limitmb=256, multisegment=True)

        count = len(all_stations)
        bar = progressbar.ProgressBar(maxval=count, widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        bar.start()

        for idx, station in enumerate(all_stations):
            bar.update(idx+1)

            self.writer.add_document(
                    name=station['name'],
                    tags=station['tags'],
                    url_resolved=station['url_resolved'],
            )

        self.writer.commit()
        print('Index successfully created!')
        bar.finish()


if __name__ == '__main__':
    ri = RadioIndex()
    print(ri.search('euro'))
    pass
