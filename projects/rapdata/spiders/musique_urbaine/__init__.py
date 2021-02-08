""" RapData MusiqueUrbaine Spiders module """

import bs4
import ratpy

from projects.rapdata.spiders.musique_urbaine.parser import Parser
from projects.rapdata.spiders.musique_urbaine import items

# ############################################################### #
# ############################################################### #


def _next_page(url, step, **kwargs):
    if url.path.split('/')[-1] == step:
        yield ratpy.Link(ratpy.URL(url.path + '/page/2'), cb_kwargs=kwargs)
    else:
        tmp = url.path.rsplit('/', 1)
        yield ratpy.Link(ratpy.URL(tmp[0] + '/' + str(int(tmp[1]) + 1)), cb_kwargs=kwargs)

# ############################################################### #


class MusiqueUrbaine(ratpy.SubSpider):

    name = 'rapdata.spiders.musiqueurbaine'
    regex = 'www\\.musiqueurbaine\\.fr'
    linker = True
    activated = True

    def __init__(self, *args, **kwargs):
        self.subspiders_cls = {
            'artists': Artists,
            'artist': Artist,
            'album': Album
        }
        ratpy.SubSpider.__init__(self, *args, **kwargs)

    def start_links(self):
        yield ratpy.URL('https://www.musiqueurbaine.fr/artistes/')

    def process_request(self, request, url, *args, **kwargs):
        if url.params != {}:
            return request.replace(url=ratpy.URL(url.path))
        else:
            return request

    def process_input(self, response, *args, **kwargs):
        res = bs4.BeautifulSoup(response.body, 'html.parser') if response else None
        [x.extract() for x in res('script')]
        [x.extract() for x in res('style')]
        return res

# ############################################################### #
# ############################################################### #


class Artists(ratpy.SubSpider):

    name = 'rapdata.spiders.musiqueurbaine.artists'
    regex = '/artistes(/page/[0-9]+)?'

    def parse(self, response, url, *args, **kwargs):
        _parser = Parser()

        for _x in _parser.parse_artists(response):
            yield ratpy.URL(_parser.parse_artist_url(_x))

        yield from _next_page(url, 'artistes')

# ############################################################### #


class Artist(ratpy.SubSpider):

    name = 'rapdata.spiders.musiqueurbaine.artist'
    regex = '/artiste/[a-z0-9-]+'

    def __init__(self, *args, **kwargs):
        self.subspiders_cls = {
            'discography': ArtistDiscography,
            'medias': ArtistMedias
        }
        ratpy.SubSpider.__init__(self, *args, **kwargs)

    def parse(self, response, url, *args, **kwargs):
        _x = response
        _parser = Parser()
        artist_or_group = ratpy.normalize(_parser.parse_artist_or_group_main_name(_x))

        artist_or_group_item = items.ArtistOrGroup(
            infos={'id': url.path.split('/')[-1], 'url': url},
            pipeline='artists/{}'.format(artist_or_group),
            names=items.ArtistOrGroup.Names(
                main=_parser.parse_artist_or_group_main_name(_x),
                others=_parser.parse_artist_or_group_other_names(_x)
            ),
            description=_parser.parse_artist_or_group_description(_x),
            origin=_parser.parse_artist_or_group_origin(_x),
            networks=items.ArtistOrGroup.Networks(
                facebook=_parser.parse_artist_or_group_facebook(_x),
                instagram=_parser.parse_artist_or_group_instagram(_x),
                twitter=_parser.parse_artist_or_group_twitter(_x),
                youtube=_parser.parse_artist_or_group_youtube(_x),
                bandcamp=_parser.parse_artist_or_group_bandcamp(_x),
                soundcloud=_parser.parse_artist_or_group_soundcloud(_x),
                snapchat=_parser.parse_artist_or_group_snapchat(_x),
                website=_parser.parse_artist_or_group_website(_x)
            ),
            picture=_parser.parse_artist_or_group_picture(_x),
            groups=_parser.parse_artist_or_group_groups(_x),
            streaming=_parser.parse_artist_or_group_streaming_url(_x)
        )
        if _parser.is_artist(_x):
            artist_or_group_item.__class__ = items.Artist
            artist_or_group_item['birth'] = items.Artist.Birth(
                name=_parser.parse_artist_birth_name(_x),
                date=_parser.parse_artist_birth_date(_x)
            )

        if _parser.is_group(_x):
            artist_or_group_item.__class__ = items.Group
            artist_or_group_item['activity'] = items.Group.Activity(
                begin=_parser.parse_group_activity_begin(_x),
                end=_parser.parse_group_activity_end(_x)
            )
            artist_or_group_item['members'] = _parser.parse_group_members(_x)

        yield artist_or_group_item
        yield ratpy.Link(ratpy.URL(url.path+'/discographie'), cb_kwargs={'artist': artist_or_group})
        yield ratpy.Link(ratpy.URL(url.path+'/medias'), cb_kwargs={'artist': artist_or_group})

# ############################################################### #


class ArtistDiscography(ratpy.SubSpider):

    name = 'rapdata.spiders.musiqueurbaine.artist.discography'
    regex = '/discographie(/page/[0-9]+)?'

    def parse(self, response, url, *args, artist='', **kwargs):
        _parser = Parser()

        for _x in _parser.parse_discography_items(response):
            yield ratpy.Link(
                ratpy.URL(_parser.parse_discography_item_url(_x)),
                cb_kwargs={'artist': artist}
            )

        yield from _next_page(url, 'discographie', artist=artist)

# ############################################################### #


class ArtistMedias(ratpy.SubSpider):

    name = 'rapdata.spiders.musiqueurbaine.artist.medias'
    regex = '/medias(/page/[0-9]+)?'

    def parse(self, response, url, *args, artist='', **kwargs):
        _parser = Parser()

        for _x in _parser.parse_medias_items(response):
            try:
                yield items.Media(
                    infos={'id': url.path.split('/')[-4], 'url': url},
                    pipeline='artist/{}'.format(artist),
                    title=_parser.parse_medias_item_title(_x),
                    type=_parser.parse_medias_item_type(_x),
                    url=_parser.parse_medias_item_url(_x)
                )
            except:
                continue

        yield from _next_page(url, 'medias', artist=artist)

# ############################################################### #
# ############################################################### #


class Album(ratpy.SubSpider):

    name = 'rapdata.spiders.musiqueurbaine.album'
    regex = '/album/[a-z0-9-]+'

    def __init__(self, *args, **kwargs):
        self.subspiders_cls = {
            'medias': AlbumMedias
        }
        ratpy.SubSpider.__init__(self, *args, **kwargs)

    def parse(self, response, url, *args, artist='',  **kwargs):
        _x = response
        _parser = Parser()
        album = ratpy.normalize(_parser.parse_album_title(_x))

        yield items.Album(
            infos={'id': url.path.split('/')[-1], 'url': url},
            pipeline='albums/{}/{}'.format(artist, album),
            title=_parser.parse_album_title(_x),
            release=_parser.parse_album_release(_x),
            format=_parser.parse_album_format(_x),
            cover=_parser.parse_album_cover(_x),
            songs=_parser.parse_album_songs(_x),
            streaming=_parser.parse_album_streaming_url(_x)
        )
        yield ratpy.Link(ratpy.URL(url.path+'/medias'), cb_kwargs={'artist': artist, 'album': album})

# ############################################################### #


class AlbumMedias(ratpy.SubSpider):

    name = 'rapdata.spiders.musiqueurbaine.album.medias'
    regex = '/medias(/page/[0-9]+)?'

    def parse(self, response, url, *args, artist='', album='', **kwargs):
        _parser = Parser()

        for _x in _parser.parse_medias_items(response):
            try:
                yield items.Media(
                    infos={'id': url.path.split('/')[-4], 'url': url},
                    pipeline='albums/{}/{}'.format(artist, album),
                    title=_parser.parse_medias_item_title(_x),
                    type=_parser.parse_medias_item_type(_x),
                    url=_parser.parse_medias_item_url(_x)
                )
            except:
                continue

        yield from _next_page(url, 'medias', artist=artist, album=album)


# ############################################################### #
# ############################################################### #
