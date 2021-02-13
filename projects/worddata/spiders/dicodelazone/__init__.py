""" WordData DicoDeLaZone Spiders module """

import bs4
import ratpy
import re

from projects.worddata.spiders.dicodelazone.parser import Parser
from projects.worddata.spiders.dicodelazone import items

# ############################################################### #
# ############################################################### #


class DicoDeLaZone(ratpy.SubSpider):

    name = 'worddata.spiders.dicodelazone'
    regex = 'dictionnairedelazone.fr'
    linker = True
    enabled = True

    def __init__(self, *args, **kwargs):
        self.subspiders_cls = {
            'lexical': DicoDeLaZoneLexical,
            'expression': DicoDeLaZoneExpression,
            'glossary': DicoDeLaZoneGlossary
        }
        ratpy.SubSpider.__init__(self, *args, **kwargs)

    def process_input(self, response, *args, **kwargs):
        res = bs4.BeautifulSoup(response.body, 'html.parser') if response else None
        [x.extract() for x in res('script')]
        [x.extract() for x in res('style')]
        return res

    def process_output(self, url, item, *args, **kwargs):
        item['website'] = 'dictionnairedelazone'
        return item

# ############################################################### #
# ############################################################### #


class DicoDeLaZoneLexical(ratpy.SubSpider):

    name = 'worddata.spiders.dicodelazone.lexical'
    regex = '/dictionary/lexical/[a-z-]'

    def __init__(self, *args, **kwargs):
        self.subspiders_cls = {
            'entry': DicoDeLaZoneLexicalEntry
        }
        ratpy.SubSpider.__init__(self, *args, **kwargs)

    def start_links(self):
        for c in range(ord('a'), ord('z')+1):
            yield 'http://dictionnairedelazone.fr/dictionary/lexical/{}'.format(chr(c))
        yield 'http://dictionnairedelazone.fr/dictionary/lexical/-'

# ############################################################### #


class DicoDeLaZoneLexicalEntry(ratpy.SubSpider):

    name = 'worddata.spiders.dicodelazone.lexical.entry'
    regex = '/[-\\w]+'

    def parse(self, response, url, *args, **kwargs):
        _parser = Parser()
        _x = response

        yield items.Word(
            infos=_parser.parse_infos(url),
            pipeline='words/{}'.format(ratpy.normalize(_parser.parse_word(_x))),
            etymology=_parser.parse_word_etymology(_x),
            usages=[
                items.Word.Usage(
                    word=_parser.parse_usage_word(usage),
                    type=_parser.parse_usage_type(usage),
                    meanings=[
                        items.Word.Meaning(
                            definition=_parser.parse_meaning_definition(meaning),
                            synonyms=_parser.parse_meaning_synonyms(meaning),
                            examples=[
                                items.Word.Example(
                                    citation=_parser.parse_example_citation(example),
                                    author=_parser.parse_example_author(example),
                                    container1=_parser.parse_example_container1(example),
                                    container2=_parser.parse_example_container2(example),
                                    date=_parser.parse_example_date(example)
                                ) for example in _parser.parse_examples(meaning)
                            ]
                        ) for meaning in _parser.parse_meanings(_x)
                    ]
                ) for usage in _parser.parse_usages(_x)
            ]
        )

# ############################################################### #
# ############################################################### #


class DicoDeLaZoneExpression(ratpy.SubSpider):

    name = 'worddata.spiders.dicodelazone.expression'
    regex = '/dictionary/locution/[a-z-]'

    def __init__(self, *args, **kwargs):
        self.subspiders_cls = {
            'entry': DicoDeLaZoneExpressionEntry
        }
        ratpy.SubSpider.__init__(self, *args, **kwargs)

    def start_links(self):
        for c in range(ord('a'), ord('z') + 1):
            yield 'http://dictionnairedelazone.fr/dictionary/locution/{}'.format(chr(c))
        yield 'http://dictionnairedelazone.fr/dictionary/locution/-'

# ############################################################### #


class DicoDeLaZoneExpressionEntry(ratpy.SubSpider):

    name = 'worddata.spiders.dicodelazone.expression.entry'
    regex = '/[-\\w]+'

# ############################################################### #
# ############################################################### #


class DicoDeLaZoneGlossary(ratpy.SubSpider):

    name = 'worddata.spiders.dicodelazone.glossary'
    regex = '/glossary/lexical/[a-z-]'

    def __init__(self, *args, **kwargs):
        self.subspiders_cls = {
            'entry': DicoDeLaZoneGlossaryEntry
        }
        ratpy.SubSpider.__init__(self, *args, **kwargs)

    def start_links(self):
        for c in range(ord('a'), ord('z')+1):
            yield 'http://dictionnairedelazone.fr/glossary/lexical/{}'.format(chr(c))
        yield 'http://dictionnairedelazone.fr/glossary/lexical/-'

# ############################################################### #


class DicoDeLaZoneGlossaryEntry(ratpy.SubSpider):

    name = 'worddata.spiders.dicodelazone.glossary.entry'
    regex = '/[-\\w]+'

# ############################################################### #
# ############################################################### #
