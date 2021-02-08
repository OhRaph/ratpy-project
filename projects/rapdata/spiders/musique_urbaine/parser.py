""" RapData MusiqueUrbaine Parser module """

import bs4
import re

import ratpy

# ############################################################### #
# ############################################################### #


class Parser(ratpy.Linker):

    # ####################################################### #
    # ####################################################### #

    def find_block_summary(self, content):
        return content.find('body').find('main').find('header').find('div', class_='bg-card')

    # ####################################################### #

    def find_block_details(self, content):
        return content.find('body').find('main').find('header').find('div').find('div').find('div').findNextSibling().find('div')

    def find_block_detail(self, content, field):
        try:
            return self.find_block_details(content).find('span', text=field).findParent().getText()[len(field)+1:]
        except:
            return ''

    # ####################################################### #

    def find_block_networks(self, content):
        return content.find('body').find('main').find('header').find('div').find('div').find('div').findNextSibling().find('div').findNextSibling()

    def find_block_network(self, content, network):
        try:
            return self.find_block_networks(content).find('a', class_=re.compile('^{}'.format(network))).get('href', '')
        except:
            return ''

    # ####################################################### #

    def find_block_streaming(self, content):
        return content.find('body').find('main').find('iframe')

    # ####################################################### #
    # ####################################################### #

    def parse_artists(self, content):
        return content.findAll('article', class_='entry')

    def parse_artist_url(self, content):
        return content.find('a').get('href', '')

    # ####################################################### #
    # ####################################################### #
    
    def parse_artist_or_group_main_name(self, content):
        try:
            return self.find_block_summary(content).find('h1', class_='entry-title').getText()
        except:
            return ''

    def parse_artist_or_group_other_names(self, content):
        return self.find_block_detail(content, 'Alias').split(', ')

    def parse_artist_or_group_description(self, content):
        try:
            return content.find('body').find('main').find('h2', text=re.compile('^Biographie')).findParent().findNextSibling().getText()
        except:
            return ''

    def parse_artist_or_group_origin(self, content):
        return self.find_block_detail(content, 'Origine')

    def parse_artist_or_group_picture(self, content):
        try:
            return self.find_block_summary(content).find('img').get('src')
        except:
            return ''

    def parse_artist_or_group_groups(self, content):
        return self.find_block_detail(content, 'Groupes').split(', ')

    def parse_artist_or_group_facebook(self, content):
        return self.find_block_network(content, 'facebook')

    def parse_artist_or_group_instagram(self, content):
        return self.find_block_network(content, 'instagram')

    def parse_artist_or_group_twitter(self, content):
        return self.find_block_network(content, 'twitter')

    def parse_artist_or_group_youtube(self, content):
        return self.find_block_network(content, 'youtube')

    def parse_artist_or_group_bandcamp(self, content):
        return self.find_block_network(content, 'bandcamp')

    def parse_artist_or_group_soundcloud(self, content):
        return self.find_block_network(content, 'soundcloud')

    def parse_artist_or_group_snapchat(self, content):
        return self.find_block_network(content, 'snapchat')

    def parse_artist_or_group_website(self, content):
        return self.find_block_network(content, 'perso')

    def parse_artist_or_group_streaming_url(self, content):
        try:
            return self.find_block_streaming(content).get('src')
        except:
            return ''

    # ####################################################### #

    def is_artist(self, content):
        return self.find_block_detail(content, 'Nom de naissance') \
            or self.find_block_detail(content, 'Naissance')

    def parse_artist_birth_name(self, content):
        return self.find_block_detail(content, 'Nom de naissance')

    def parse_artist_birth_date(self, content):
        return self.find_block_detail(content, 'Naissance')

    # ####################################################### #

    def is_group(self, content):
        return self.find_block_detail(content, 'Formation')  \
            or self.find_block_detail(content, 'Séparation') \
            or self.find_block_detail(content, 'Membres')

    def parse_group_activity_begin(self, content):
        return self.find_block_detail(content, 'Formation')

    def parse_group_activity_end(self, content):
        return self.find_block_detail(content, 'Séparation')

    def parse_group_members(self, content):
        return self.find_block_detail(content, 'Membres').split(', ')

    # ####################################################### #
    # ####################################################### #

    def parse_discography_items(self, content):
        return content.findAll('article', class_='entry')

    def parse_discography_item_url(self, content):
        return content.find('header').find('a').get('href', '')

    # ####################################################### #
    # ####################################################### #

    def parse_medias_items(self, content):
        return content.findAll('article', class_='entry')

    def parse_medias_item_title(self, content):
        return content.find('h2').getText()

    def parse_medias_item_type(self, content):
        return content.find('div', class_='small').getText()

    def parse_medias_item_url(self, content):
        return content.find('a').get('href', '')

    # ####################################################### #
    # ####################################################### #

    def parse_album_title(self, content):
        try:
            return self.find_block_summary(content).find('h1', class_='entry-title').find('span', class_='main').getText()
        except:
            return ''

    def parse_album_release(self, content):
        return self.find_block_detail(content, 'Sortie')

    def parse_album_format(self, content):
        return self.find_block_detail(content, 'Format')

    def parse_album_cover(self, content):
        try:
            return self.find_block_summary(content).find('img').get('src')
        except:
            return ''

    def parse_album_songs(self, content):
        res = []
        try:
            for cd in content.find('h2', text='Tracklist').findParent().findNextSibling().findAll('p'):
                for song in cd.children:
                    if isinstance(song, bs4.element.NavigableString):
                        res.append(song.strip())
            return res
        except:
            return []

    def parse_album_streaming_url(self, content):
        try:
            return self.find_block_streaming(content).get('src')
        except:
            return ''

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
