import json
from urllib.request import urlopen
from urllib.parse import quote


BASE_SEARCH_URL = 'http://de1.api.radio-browser.info/json/stations/byname/{}'
BASE_CATEGORY_SEARCH_URL = 'http://de1.api.radio-browser.info/json/stations/bytag/{}'
BASE_ALL_CATEGORY_URL = 'http://de1.api.radio-browser.info/json/tags'
ALL_STATIONS_URL = 'http://de1.api.radio-browser.info/json/stations'


class RadioBrowse(object):
    """
    Simple API to radio-browser.info
    """

    def __init__(self):
        pass

    def search(self, term):
        """
        Search for a term
        :param term:
        :return: search result
        """
        url = BASE_SEARCH_URL.format(quote(term))
        json_data = urlopen(url).read().decode()
        result = json.loads(json_data)
        return result

    def categories(self):
        """
        Get all Categories
        :return: categories
        """
        url = BASE_ALL_CATEGORY_URL
        json_data = urlopen(url).read().decode()
        result = json.loads(json_data)
        return result

    def search_category(self, term):
        """
        Search for a category by a given term
        :param term:
        :return: search result
        """
        url = BASE_CATEGORY_SEARCH_URL.format(quote(term))
        json_data = urlopen(url).read().decode()
        result = json.loads(json_data)
        return result

    def all_stations(self):
        """
        Return all stations
        :return: All stations
        """
        json_data = urlopen(ALL_STATIONS_URL).read().decode()
        result = json.loads(json_data)
        return result


if __name__ == '__main__':
    rb = RadioBrowse()
    res = rb.search('EKR')
    print(res)




