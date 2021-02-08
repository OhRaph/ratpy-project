""" WordData Dico2Rue Parser module """

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
        return content.find('table').findAll('tr')[0].find('td', class_=re.compile('^word ')).find('a').get('href')

    # ####################################################### #

    def parse_infos(self, content):
        return {
            'id': self.get_id(content),
            'url': self.get_href(content)
        }

    # ####################################################### #

    def parse_words(self, content):
        return content.findAll('div', class_='words')

    # ####################################################### #

    def parse_word(self, content):
        return content.find('table').findAll('tr')[0].find('td', class_=re.compile('^word ')).find('a').getText()

    def parse_definition(self, content):
        res = ''
        for _x in content.find('table').findAll('tr')[1].find('td'):
            if isinstance(_x, bs4.element.NavigableString):
                tmp = _x.strip()
                if tmp != '':
                    res = res + tmp + '\n'
        return res

    def parse_example(self, content):
        _x = content.find('table').findAll('tr')[2].find('td', class_=re.compile('^example ')).getText().strip().strip('"').strip()
        return _x + '\n' if _x != '' else ''

    # ####################################################### #

    def is_last_page(self, content):
        tmp = content.find('div', id='pagination')
        return tmp.find('span', class_='current').findNextSibling() is None if tmp else True

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #

