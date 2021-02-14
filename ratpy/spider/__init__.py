""" Ratpy Spider module """

import ast
import os
import scrapy

from ratpy.utils import Utils, Attribute
from ratpy.utils.index import Index

from ratpy.http.request import Request
from ratpy.http.url import URL
from ratpy.link import Link
from ratpy.item import Item
from ratpy.spider.subspider import SubSpider, init_subspiders, SUBSPIDERS_CLS_ERROR

__all__ = ['Spider', 'SubSpider']

# ############################################################### #
# ############################################################### #


class Spider(Utils, scrapy.Spider):

    """ Ratpy Spider class """

    # ####################################################### #
    # ####################################################### #

    name = 'ratpy.spider'

    directory = None
    crawler = None
    custom_settings = None

    linker = True

    subspiders_cls = {}
    subspiders = None

    _start_url = None
    _start_requests = None

    _index_items = None

    # ####################################################### #

    def __init__(self, crawler, *args, start_url=None, start_requests=None, **kwargs):

        self.directory = os.path.join('spiders', self.name)
        self.crawler = crawler
        Utils.__init__(self, self.crawler, directory=self.directory)
        scrapy.Spider.__init__(self, *args, **kwargs)

        self.linker = self.get_attribute('linker')

        self.subspiders = init_subspiders(self.get_attribute('subspiders_cls'), self, self.name, *args, **kwargs)

        self._index_items = Index(self.crawler, directory=self.directory, name=self.name+'.items', columns=['url', 'value'])

        if start_url:
            self._start_url = self._create_start_request(start_url, *args, **kwargs)
        if start_requests:
            self._start_requests = start_requests

        self.logger.info('{:_<18} : OK   COMMAND = {}'.format('Initialisation', self.crawler.settings['COMMAND']))

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(crawler, *args, **kwargs)
        crawler.signals.connect(spider.open, signal=scrapy.signals.spider_opened)
        crawler.signals.connect(spider.close, signal=scrapy.signals.spider_closed)
        return spider

    @classmethod
    def update_settings(cls, settings):
        settings.setdict(cls.custom_settings or {}, priority='spider')

    # ####################################################### #

    @staticmethod
    def possible_attributes():
        res = super(Spider, Spider).possible_attributes()
        res.update([
            Attribute('linker', bool, False),
            Attribute('subspiders_cls', (type, dict), {})
            ])
        return res

    @property
    def infos(self):
        infos = super().infos
        infos['linker'] = self.linker
        infos['start_url'] = self._start_url.infos if self._start_url else None
        infos['start_requests'] = 'overwritten' if self._start_requests else 'default'
        infos['subspiders'] = self.subspiders.infos
        return infos

    # ####################################################### #

    def open(self, *args, **kwargs):
        self.logger.debug('{:_<18}'.format('Open'))

        self._index_items.open()

        self.logger.info('{:_<18} : OK'.format('Open'))

        if self.linker is False:
            self.logger.warning('LINKER SET TO FALSE !')

    def close(self, reason, *args, **kwargs):
        self.logger.debug('{:_<18}'.format('Close'))

        self._index_items.close()

        self.logger.info('{:_<18} : OK   REASON = {}'.format('Close', reason))

    # ####################################################### #
    # ####################################################### #

    def _create_start_request(self, url, *args, **kwargs):

        try:
            args = [ast.literal_eval(value) for value in args]
        except ValueError:
            args = []
            self.logger.error("Unable to evaluate 'args' !")

        try:
            kwargs = {key: ast.literal_eval(value) for key, value in kwargs.items()}
        except ValueError:
            kwargs = {}
            self.logger.error("Unable to evaluate 'kwargs' !")

        return Link(url, *args, **kwargs)

    def start_requests(self):

        if self._start_url:
            if self._start_url.kwargs.get('callback') is not None:
                self.logger.warning('Request callback reset to default !')
            self._start_url.kwargs['callback'] = self.parse

            self.logger.info('{:_<18} : {} {}'.format('Request URL', self._start_url.url.path, self._start_url.url.params))
            self.logger.info('{:_<18} : {}'.format('Request args', self._start_url.args))
            self.logger.info('{:_<18} : {}'.format('Request kwargs', self._start_url.kwargs))
            yield from Request.create(self._start_url)

        elif self._start_requests:
            yield from self._start_requests()

        else:
            for link in self.subspiders.start_links_():
                yield from Request.create(link)

    # ####################################################### #

    @classmethod
    def handles_request(cls, request):

        url = URL(request.url)

        if isinstance(cls.subspiders_cls, SubSpider):
            return cls.subspiders_cls.handles(url)
        elif isinstance(cls.subspiders_cls, dict):
            return any(subspider_cls.handles(url) for subspider_cls in cls.subspiders_cls)
        else:
            raise TypeError(SUBSPIDERS_CLS_ERROR)

    # ####################################################### #
    # ####################################################### #

    def parse(self, response, *args, **kwargs):

        url = URL(response.url if response is not None else '')

        self.logger.debug('{:_<18} :      {} {}'.format('Parse', url.path, url.params))

        if len(url.remaining) > 0:
            self.logger.debug('New parse !')

            results = self.subspiders.parse_(response, url, *args, **kwargs)
            for result in results:
                if isinstance(result, Item):
                    self.logger.debug('Item OK !')
                    self._index_items.add(url=url, value=result['pipeline'])
                    # print(result)
                    yield result

                elif isinstance(result, URL):
                    self.logger.debug('URL OK !')
                    link = Link.create(result)
                    requests = Request.create(link, origin=url)
                    yield from requests if self.linker else []

                elif isinstance(result, Link):
                    self.logger.debug('Link OK !')
                    requests = Request.create(result, origin=url)
                    yield from requests if self.linker else []

                elif isinstance(result, Request):
                    self.logger.debug('Request OK !')
                    yield from [result] if self.linker else []
                else:
                    self.logger.debug('Other result !')
                    yield from []

        self.logger.debug('{:_<18} : OK   {} {}'.format('Parse', url.path, url.params))

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
