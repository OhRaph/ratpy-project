""" RapData GeniusUI Spiders module """

import bs4
import ratpy

from projects.rapdata.spiders.genius.ui.parser import Parser
from projects.rapdata.spiders.genius import items


# ############################################################### #
# ############################################################### #


class GeniusUI(ratpy.SubSpider):

    name = 'rapdata.spiders.genius.ui'
    regex = 'genius\\.com'
    linker = True
    activated = True

    def __init__(self, *args, **kwargs):
        self.subspiders_cls = {
            'artist': GeniusUIArtist,
            'album': GeniusUIAlbum,
            'lyrics': GeniusUILyrics,
            'artist_videos': GeniusUIArtistVideos
        }
        ratpy.SubSpider.__init__(self, *args, **kwargs)

    def process_input(self, response, *args, **kwargs):
        res = bs4.BeautifulSoup(response.body, 'html.parser') if response else None
        [x.extract() for x in res('script')]
        [x.extract() for x in res('style')]
        return res

# ############################################################### #
# ############################################################### #


class GeniusUIArtist(ratpy.SubSpider):

    name = 'rapdata.spiders.genius.ui.artist'
    regex = '/artists/[0-9]+'

# ############################################################### #


class GeniusUIArtistVideos(ratpy.SubSpider):

    name = 'rapdata.spiders.genius.ui.artist.videos'
    regex = '/Genius-france-videotheque-[-_\\w]*'

# ############################################################### #
# ############################################################### #


class GeniusUIAlbum(ratpy.SubSpider):

    name = 'rapdata.spiders.genius.ui.album'
    regex = '/albums/[0-9]+/[0-9]+'


# ############################################################### #
# ############################################################### #


class GeniusUILyrics(ratpy.SubSpider):

    name = 'rapdata.spiders.genius.ui.song.lyrics'
    regex = '/[-_\\w]*-lyrics'

    def enqueue_request(self, request, *args, **kwargs):
        return bool(request.cb_kwargs.get('artist', '') and request.cb_kwargs.get('music', ''))

    def parse(self, response, *args, artist='', music='', **kwargs):
        _x = response
        _parser = Parser()

        yield items.Music.Lyrics(
            infos=_parser.parse_info(_x),
            pipeline='musics/{}/{}'.format(artist, music),
            title=_parser.parse_title(_x),
            lyrics=_parser.parse_lyrics(_x),
            annotations=_parser.parse_lyrics_annotations(_x, cb_kwargs={'artist': artist, 'music': music})
        )
        yield from _parser.links

# ############################################################### #
# ############################################################### #
