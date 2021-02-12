""" RapData GeniusAPI Spiders module """

import json
import os
import ratpy

from projects.rapdata.spiders.genius.api.parser import Parser
from projects.rapdata.spiders.genius import items


# ############################################################### #
# ############################################################### #


def read_token(settings):
    with open(os.path.join(ratpy.resources_directory(settings), 'genius.api.token'), 'r') as file:
        token = file.read()
        file.close()
    return token


class GeniusAPI(ratpy.SubSpider):

    name = 'rapdata.spiders.genius.api'
    regex = 'api\\.genius\\.com'
    linker = True
    activated = True

    def __init__(self, spider, *args, **kwargs):
        self.subspiders_cls = {
            'artist': GeniusAPIArtist,
            'album': GeniusAPIAlbum,
            'song': GeniusAPISong,
            'annotation': GeniusAPIAnnotation
        }
        self.token = read_token(spider.crawler.settings)
        ratpy.SubSpider.__init__(self, spider, *args, **kwargs)

    def start_links(self):
        yield ratpy.URL('https://api.genius.com/artists/1282')

    def process_request(self, request, *args, **kwargs):
        headers = request.headers
        headers['Authorization'] = self.token
        request = request.replace(headers=headers)
        return request

    def process_input(self, response, *args, **kwargs):
        return json.loads(response.body).get('response', {})

# ############################################################### #
# ############################################################### #


class GeniusAPIArtist(ratpy.SubSpider):

    name = 'rapdata.spiders.genius.api.artist'
    regex = '/artists/[0-9]+'

    def __init__(self, *args, **kwargs):
        self.subspiders_cls = {
            'songs': GeniusAPIArtistSongs
        }
        ratpy.SubSpider.__init__(self, *args, **kwargs)

    def parse(self, response, url, *args, **kwargs):
        _x = response['artist']
        _parser = Parser()
        artist = ratpy.normalize(_x['name'])

        _parser.add_link(
            ratpy.Link(
                ratpy.URL(url.path+'/songs', page='1'),
                priority=1,
                cb_kwargs={'artist': artist}
            )
        )
        yield items.Artist(
            infos=_parser.parse_info(_x),
            pipeline='artists/{}'.format(artist),
            names=items.Artist.Names(
                main=_x['name'],
                others=_x['alternate_names']
            ),
            description=_parser.parse_html(_x['description']['dom'], linker=True),
            social=items.Artist.Social(
                followers=_x['followers_count'],
                networks=items.Artist.Social.Networks(
                    facebook=_x['facebook_name'],
                    instagram=_x['instagram_name'],
                    twitter=_x['twitter_name']
                )
            ),
            verified=_x['is_verified'],
            picture=_x['image_url']
        )
        yield from _parser.links

# ############################################################### #


class GeniusAPIArtistSongs(ratpy.SubSpider):

    name = 'rapdata.spiders.genius.api.artist.songs'
    regex = '/songs'

    def enqueue_request(self, request, *args, **kwargs):
        return bool(request.cb_kwargs.get('artist', ''))

    def process_request(self, request, *args, **kwargs):
        return request.replace(url=ratpy.URL(request.url, sort='title', per_page='50'))

    def parse(self, response, url, *args, artist='', **kwargs):
        _x = response['songs']
        _parser = Parser()

        if _x:
            _parser.add_link(
                ratpy.Link(
                    ratpy.URL(url.path, page=str(int(url.params['page'])+1)),
                    priority=int(url.params['page']),
                    cb_kwargs={'artist': artist}
                )
            )
        yield items.Artist.Songs(
            infos=url.split('/')[-2],
            pipeline='artists/{}'.format(artist),
            page=url.params['page'],
            songs=_parser.parse_artist_songs(_x, artist=artist)
        )
        yield from _parser.links

# ############################################################### #
# ############################################################### #


class GeniusAPIAlbum(ratpy.SubSpider):

    name = 'rapdata.spiders.genius.api.album'
    regex = '/albums/[0-9]+'

    def enqueue_request(self, request, *args, **kwargs):
        return bool(request.cb_kwargs.get('artist', ''))

    def parse(self, response, *args, artist='', **kwargs):
        _x = response['album']
        _parser = Parser()
        album = ratpy.normalize(_x['name'])

        yield items.Album(
            infos=_parser.parse_info(_x),
            pipeline='albums/{}/{}'.format(artist, album),
            titles=items.Album.Titles(
                main=_x['name'],
                others=[]
            ),
            description=_parser.parse_htmls(_x['description_annotation']['annotations'], linker=False),
            release=_x['release_date'],
            cover=_x['cover_art_url'],
            artists=items.Album.Artists(
                main=_parser.parse_id(_x['artist']),
                others=_parser.parse_artists(_x['song_performances'])
            )
        )
        yield from _parser.links


# ############################################################### #
# ############################################################### #


class GeniusAPISong(ratpy.SubSpider):

    name = 'rapdata.spiders.genius.api.song'
    regex = '/songs/[0-9]+'

    def enqueue_request(self, request, *args, **kwargs):
        return bool(request.cb_kwargs.get('artist', ''))

    def parse(self, response, *args, artist='', **kwargs):
        _x = response['song']
        _parser = Parser()
        music = ratpy.normalize(_x['title'])

        _parser.add_link(
            ratpy.Link(
                _parser.parse_url(_x),
                priority=10,
                cb_kwargs={'artist': artist, 'music': music}
            )
        )

        yield items.Music(
            infos=_parser.parse_info(_x),
            pipeline='musics/{}/{}'.format(artist, music),
            titles=items.Music.Titles(
                main=_x['title'],
                others=[_x['title_with_featured']]
            ),
            description=_parser.parse_html(_x['description']['dom'], linker=False),
            release=_x['release_date'],
            artists=items.Music.Artists(
                main=_parser.parse_id(_x['primary_artist']),
                feat=_parser.parse_ids(_x['featured_artists']),
                prod=_parser.parse_ids(_x['producer_artists']),
                write=_parser.parse_ids(_x['writer_artists']),
                others=_parser.parse_artists(_x['custom_performances'])
            ),
            album=_parser.parse_id(_x['album'], cb_kwargs={'artist': artist}) if 'album' in _x else -1,
            status=_x['lyrics_state'],
            relations=_parser.parse_song_relations(_x['song_relationships'])
        )
        yield from _parser.links

# ############################################################### #
# ############################################################### #


class GeniusAPIAnnotation(ratpy.SubSpider):

    name = 'rapdata.spiders.genius.api.annotation'
    regex = '/annotations/[0-9]+'

    def enqueue_request(self, request, *args, **kwargs):
        return bool(request.cb_kwargs.get('artist', '') and request.cb_kwargs.get('music', ''))

    def parse(self, response, *args, artist='', music='', **kwargs):
        _x = response['annotation']
        _parser = Parser()

        yield items.Music.Lyrics.Annotation(
            infos=_parser.parse_info(_x),
            pipeline='musics/{}/{}'.format(artist, music),
            body=_parser.parse_html(_x['body']['dom']),
            pinned=_x['pinned'],
            state=_x['state']
        )
        yield from _parser.links


# ############################################################### #
# ############################################################### #
