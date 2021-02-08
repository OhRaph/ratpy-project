""" RapData UnderCream Parser module """

import re
import bs4

import ratpy

# ############################################################### #
# ############################################################### #


class Parser(ratpy.Linker):

    # ####################################################### #
    # ####################################################### #

    def get_id(self, content):
        return self.get_href(content).split('/')[-2]

    def get_href(self, content):
        return content.find('h1').find('a').get('href', '')

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
                x = x[0:search.start()]

            search = re.search(r' \[', x)
            if search:
                x = x[0:search.start()]

            return x

        x = content.find('h1').find('a').getText().split(' – ', 1)
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
        x = content.find('h1').find('a').getText()
        try:
            return int(re.sub(r'.*\(.*(\d{4}).*', r'\1', x))
        except:
            return None

    def parse_album_cover(self, content):
        try:
            return content.findAll('div')[2].findAll('p')[0].find('img').get('src')
        except:
            return ''

    # ####################################################### #

    def parse_album_songs(self, content):

        res = []
        for i in range(1, 4):
            try:
                for block in content.findAll('div')[2].findAll('p')[i]:
                    if isinstance(block, bs4.element.NavigableString):
                        res.append(block.strip())
                if len(res) > 1:
                    break
                else:
                    res = []
            except:
                continue
        if len(res):
            return res
        else:
            raise Exception

    # ####################################################### #

    def parse_albums(self, content):
        return content.findAll('article', class_=re.compile('^art-post art-article post-'))

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
