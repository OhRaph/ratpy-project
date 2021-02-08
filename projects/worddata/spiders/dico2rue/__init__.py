""" WordData Dico2Rue Spiders module """

import bs4
import ratpy
import re

from projects.worddata.spiders.dico2rue.parser import Parser
from projects.worddata.spiders.dico2rue import items

# ############################################################### #
# ############################################################### #


class Dico2Rue(ratpy.SubSpider):

    name = 'worddata.spiders.dico2rue'
    regex = 'www.dico2rue.com/dictionnaire/alphabet/[A-Z](/page-[0-9]+)?'
    linker = True
    activated = True

    def __init__(self, *args, **kwargs):
        ratpy.SubSpider.__init__(self, *args, **kwargs)

    def start_links(self):
        for c in range(ord('A'), ord('Z')+1):
            yield 'http://www.dico2rue.com/dictionnaire/alphabet/{}'.format(chr(c))

    def process_input(self, response, *args, **kwargs):
        res = bs4.BeautifulSoup(response.body, 'html.parser') if response else None
        [x.extract() for x in res('script')]
        [x.extract() for x in res('style')]
        return res

    def parse(self, response, url, *args, **kwargs):
        _parser = Parser()

        for _x in _parser.parse_words(response):
            yield items.Word(
                infos=_parser.parse_infos(_x),
                pipeline='words/{}'.format(ratpy.normalize(_parser.parse_word(_x))),
                word=_parser.parse_word(_x),
                definition=_parser.parse_definition(_x),
                example=_parser.parse_example(_x)
            )

        if not _parser.is_last_page(response):
            if not re.search(r'page-[0-9]*', url.path.split('/')[-1]):
                yield ratpy.Link(ratpy.URL(url.path + '/page-2'))
            else:
                tmp = url.path.rsplit('-', 1)
                yield ratpy.Link(ratpy.URL(tmp[0] + '-' + str(int(tmp[1]) + 1)))

# ############################################################### #
# ############################################################### #
