""" RapData Frap Parser module """

import re
import bs4

import ratpy

# ############################################################### #
# ############################################################### #


class Parser(ratpy.Linker):

    # ####################################################### #
    # ####################################################### #

    def get_id(self, content):
        return self.get_href(content).split('/')[-1].replace('.html', '')

    def get_href(self, content):
        return content.find('div', class_='t_cat').find('a').get('href', '')

    # ####################################################### #

    def parse_infos(self, content):
        return {
            'id': self.get_id(content),
            'url': self.get_href(content)
        }

    # ####################################################### #

    def _split(self, content):

        def _extract_album_name(x):
            search = re.search(r' \(\d{4}', x)
            if search:
                return x[0:search.start()]

            search = re.search(r' \(.*\d{4}', x)
            if search:
                return x[0:search.start()]

            return x

        x = content.find('div', class_='t_cat').find('a').getText().split(' - ', 1)
        if len(x) == 1:
            if re.search(r' -$', x[0]):
                tmp = re.sub(r' -$', '', x[0])
                return tmp, tmp
            else:
                return '', _extract_album_name(x[0])
        else:
            return x[0], _extract_album_name(x[1])

    def parse_album_title(self, content):
        _, res = self._split(content)
        return res

    def parse_album_artist_name(self, content):
        res, _ = self._split(content)
        return res

    # ####################################################### #

    def parse_album_notation(self, content):
        return int(content.find('li', class_="current-rating").getText())/17

    def parse_album_release(self, content):
        x = content.find('div', class_='t_cat').find('a').getText()
        try:
            return int(re.sub(r'.*\(.*(\d{4}).*', r'\1', x))
        except:
            if re.search(r'\d{4}', x):
                return int(re.sub(r'.*(\d{4}).*', r'\1', x))
            else:
                return None

    def parse_album_cover(self, content):
        try:
            return content.find('div', class_='cat_text').find('img').get('src')
        except:
            return ''

    # ####################################################### #

    def find_parse_album_songs_method(self, content):
        try:
            content.find('div', class_='more').findNext('table').findAll('tr')[1].find('td')
            return 1
        except:
            content.find('div', class_='cat_text').find('div')
            return 2

    def find_album_songs_method_1(self, content):
        return content.find('div', class_='more').findNext('table').findAll('tr')[1].find('td')

    def find_album_songs_method_2(self, content):
        return content.find('div', class_='cat_text').find('div')

    def parse_album_songs(self, content):

        res = []

        if self.find_parse_album_songs_method(content) == 1:
            content = self.find_album_songs_method_1(content)
        elif self.find_parse_album_songs_method(content) == 2:
            content = self.find_album_songs_method_2(content)
        else:
            return res

        for block in content:
            if isinstance(block, bs4.element.NavigableString):
                res.append(block.strip())
        return res

    # ####################################################### #

    def parse_albums(self, content):
        return content.findAll('div', class_='cat')

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
