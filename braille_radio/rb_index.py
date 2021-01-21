import os, os.path
from whoosh import index
from whoosh.fields import Schema, NGRAM, ID
from braille_radio.radiobrowse import RadioBrowse
from whoosh.qparser import MultifieldParser
from os.path import expanduser

home = expanduser("~")

INDEX_DIR = home + "/braille_radio_index_dir"

class RadioIndex(object):

    def __init__(self):
        self.schema = Schema(
                name=NGRAM(stored=True),
                tags=NGRAM(stored=True),
                url_resolved=ID(stored=True)
        )

        if not os.path.exists(INDEX_DIR):
            os.mkdir(INDEX_DIR)

        if index.exists_in(INDEX_DIR):
            self.ix = index.open_dir(INDEX_DIR)
        else:
            self.ix = index.create_in(INDEX_DIR, self.schema)
            self.index_stations()

    def index_stations(self):
        print('Creating station index. This takes a minute or two...')
        rb = RadioBrowse()
        all_stations = rb.all_stations()

        self.writer = self.ix.writer()

        for station in all_stations:

            self.writer.add_document(
                    name=station['name'],
                    tags=station['tags'],
                    url_resolved=station['url_resolved'],
            )

        self.writer.commit()
        print('Index successfully created!')

    def search(self, term):
        qp = MultifieldParser(['name','tags'], schema=self.schema)
        q = qp.parse(term)

        searcher = self.ix.searcher()
        results = searcher.search(q, limit=None)
        return results


if __name__ == '__main__':
    ri = RadioIndex()
    print(ri.search('euro'))
    pass
