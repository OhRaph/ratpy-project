
import bs4
import random
import subprocess
import sys
import time

from urllib.parse import urlencode

from scrapy.commands import ScrapyCommand as RatpyCommand
from scrapy.linkextractors import LinkExtractor

import ratpy


__all__ = ['RatpyCommand','TestEnvironment', 'TestSpider', 'set_command']

# ############################################################### #
# ############################################################### #


def set_command(command):
    command.crawler_process.settings['COMMAND'] = command.name


# ############################################################### #
# ############################################################### #


class TestEnvironment(object):

    """ Ratpy Test Environment class """

    def __enter__(self):
        from scrapy.utils.test import get_testenv
        pargs = [sys.executable, '-u', '-m', 'ratpy.utils.server']
        self.proc = subprocess.Popen(pargs, stdout=subprocess.PIPE, env=get_testenv())
        self.proc.stdout.readline()

    def __exit__(self, exc_type, exc_value, traceback):
        self.proc.kill()
        self.proc.wait()
        time.sleep(0.2)

# ############################################################### #
# ############################################################### #


class TestSpider(ratpy.Spider):

    name = 'ratpy.spider.test.crawler'

    link_extractor = LinkExtractor()

    request_url = None

    def __init__(self, crawler, *args, **kwargs):
        ratpy.Spider.__init__(self, crawler, *args, **kwargs)
        self.request_url = self.create_random_url(crawler.settings)

    def parse(self, response, *args, **kwargs):
        yield TestItem(
            infos=response.url,
            pipeline='nothingness',
            content=' '.join(bs4.BeautifulSoup(response.body, 'html.parser').get_text().split('Link to page'))
        )
        for link in self.link_extractor.extract_links(response):
            url = ratpy.URL(link.url)
            yield ratpy.Request(url=url, callback=self.parse)

    @classmethod
    def create_random_url(cls, settings):
        server_url = settings.get('TEST_SERVER_URL')
        server_nb_pages = int(settings.get('TEST_SERVER_NB_PAGES'))
        server_nb_page_links = int(settings.get('TEST_SERVER_NB_PAGE_LINKS'))
        request_params = {
            'nb_pages': server_nb_pages,
            'nb_page_links': server_nb_page_links,
            'page': random.randint(1, server_nb_pages)
        }
        return ratpy.URL('{}?{}'.format(server_url, urlencode(request_params, doseq=True)))


# ############################################################### #
# ############################################################### #

class TestItem(ratpy.Item):

    content = ratpy.Field()


# ############################################################### #
# ############################################################### #
