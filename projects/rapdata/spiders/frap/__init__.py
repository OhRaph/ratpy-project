""" RapData Frap Spiders module """

import bs4
import ratpy

from projects.rapdata.spiders.frap.parser import Parser
from projects.rapdata.spiders.frap import items

# ############################################################### #
# ############################################################### #


def _next_page(url):
    x = url.path.rsplit('/', 1)
    yield ratpy.URL(x[0] + '/' + str(int(x[1]) + 1))


def _calc_interval(url, nb_pages=10, default_interval=2, **kwargs):
    x = int(url.path.rsplit('/', 1)[1]) - 1
    yield ratpy.Interval(str((nb_pages - x) * default_interval) + 'd', **kwargs)

# ############################################################### #


class Frap(ratpy.SubSpider):

    name = 'rapdata.spiders.frap'
    regex = 'frap\\.ru(/page/[0-9]+)?'
    linker = True
    enabled = True

    def __init__(self, *args, **kwargs):
        ratpy.SubSpider.__init__(self, *args, **kwargs)

    def start_links(self):
        yield ratpy.URL('https://frap.ru')

    def process_request(self, request, url, *args, **kwargs):
        tmp = url.path.split('/')
        if tmp[-1] == 'frap.ru':
            return request.replace(url=ratpy.URL(url.path+'/page/1'))
        else:
            return request

    def process_input(self, response, *args, **kwargs):
        res = bs4.BeautifulSoup(response.body, 'html.parser') if response else None
        [x.extract() for x in res('script')]
        [x.extract() for x in res('style')]
        return res

    def parse(self, response, url, *args, **kwargs):
        _parser = Parser()

        for _x in _parser.parse_albums(response):

            artist = ratpy.normalize(_parser.parse_album_artist_name(_x))
            album = ratpy.normalize(_parser.parse_album_title(_x))

            try:
                yield items.Album(
                    infos=_parser.parse_infos(_x),
                    pipeline='albums/{}/{}'.format(artist, album),
                    title= _parser.parse_album_title(_x),
                    artist=_parser.parse_album_artist_name(_x),
                    notation=_parser.parse_album_notation(_x),
                    release=_parser.parse_album_release(_x),
                    cover=_parser.parse_album_cover(_x),
                    songs=_parser.parse_album_songs(_x)
                )
            except:
                # print(url, artist, album)
                continue

        yield from _next_page(url)
        yield from _calc_interval(url)

    def process_output(self, url, item, *args, **kwargs):
        item['website'] = 'frap'
        return item

# ############################################################### #
# ############################################################### #
