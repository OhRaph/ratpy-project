""" RapData Frap Spiders module """

import bs4
import ratpy

from projects.rapdata.spiders.frap.parser import Parser
from projects.rapdata.spiders.frap import items

# ############################################################### #
# ############################################################### #


class Frap(ratpy.SubSpider):

    name = 'rapdata.spiders.frap'
    regex = 'frap\\.ru(/page/[0-9]+)?'
    linker = True
    activated = True

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

        tmp = url.path.rsplit('/', 1)
        yield ratpy.URL(tmp[0]+'/'+str(int(tmp[1])+1))

    def process_output(self, url, item, *args, **kwargs):
        item['website'] = 'frap'
        return item

# ############################################################### #
# ############################################################### #
