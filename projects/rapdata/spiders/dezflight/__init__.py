""" RapData DezFlight Spiders module """

import bs4
import ratpy

from projects.rapdata.spiders.dezflight.parser import Parser
from projects.rapdata.spiders.dezflight import items

# ############################################################### #
# ############################################################### #


class DezFlight(ratpy.SubSpider):

    name = 'rapdata.spiders.dezflight'
    regex = 'dezflight-underground\\.com/category/albums-in-french(/page/[0-9]+)?'
    linker = True
    activated = True

    def __init__(self, *args, **kwargs):
        ratpy.SubSpider.__init__(self, *args, **kwargs)

    def start_links(self):
        yield ratpy.URL('http://dezflight-underground.com/category/albums-in-french')

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
                    release=_parser.parse_album_release(_x),
                    cover=_parser.parse_album_cover(_x),
                    songs=_parser.parse_album_songs(_x)
                )
            except:
                # print(url, artist, album)
                continue

        if url.path.split('/')[-1] == 'albums-in-french':
            yield ratpy.Link(ratpy.URL(url.path + '/page/2'))
        else:
            tmp = url.path.rsplit('/', 1)
            yield ratpy.Link(ratpy.URL(tmp[0] + '/' + str(int(tmp[1]) + 1)))

# ############################################################### #
# ############################################################### #
