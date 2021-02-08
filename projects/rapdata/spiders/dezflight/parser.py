""" RapData DezFlight Parser module """

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
        return content.find('h2', class_='title').find('a').get('href', '')

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

        x = content.find('h2', class_='title').find('a').getText().split(' – ', 1)
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

    def parse_album_release(self, content):
        x = content.find('h2', class_='title').find('a').getText()
        try:
            return int(re.sub(r'.*\(.*(\d{4}).*', r'\1', x))
        except:
            return None

    def parse_album_cover(self, content):
        try:
            return content.find('div', class_='article_main').find('img').get('src')
        except:
            return ''

    # ####################################################### #

    def parse_album_songs(self, content):

        res = []
        for block in content.find('div', class_='article_main').findAll('p')[2]:
            if isinstance(block, bs4.element.NavigableString):
                res.append(block.strip())
        return res

    # ####################################################### #

    def parse_albums(self, content):
        return content.findAll('article', class_='article')

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
