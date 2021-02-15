""" Ratpy SubSpider module """

import inspect
import json
import os
import scrapy
import time

from collections.abc import Iterable

from ratpy.utils import Utils, Attribute, Function, monitored
from ratpy.utils.index import Index
from ratpy.http.request import Request, IgnoreRequest
from ratpy.http.response import Response, IgnoreResponse
from ratpy.http.url import URL
from ratpy.link import Link
from ratpy.item import Item
from ratpy.interval import Interval

__all__ = [
    'SubSpider', 'init_subspiders', 'SUBSPIDERS_CLS_ERROR',
    'Link', 'URL', 'Item'
]

# ############################################################### #
# ############################################################### #


SUBSPIDERS_CLS_ERROR = 'Invalid type for attribute \'subspiders_cls\' : use class SubSpider or dict.'

START, STOP, DISABLED = object(), object(), object()


def init_subspiders(subspiders_cls, crawler, spider, name, *args, **kwargs):
    if inspect.isclass(subspiders_cls):
        subspiders = subspiders_cls.from_spider(crawler, spider, *args, **kwargs)
    elif isinstance(subspiders_cls, dict):
        subspiders = SubSpider.from_spider(crawler, spider, *args, name=name, subspiders_cls=subspiders_cls, **kwargs)
    else:
        raise TypeError(SUBSPIDERS_CLS_ERROR)
    return subspiders

# ############################################################### #


@monitored
class SubSpider(Utils):

    """ Ratpy SubSpider class """

    # ####################################################### #
    # ####################################################### #

    name = 'ratpy.subspider'

    directory = None
    crawler = None
    spider = None

    enabled = True
    linker = True
    regex = ''
    interval = 0

    subspiders_cls = {}
    subspiders = None

    _state = None
    _index_status = None
    _index_items = None

    # ####################################################### #

    def __init__(self, crawler, spider, *args, **kwargs):
        self.crawler = crawler
        self.spider = spider

        self.directory = os.path.join(self.spider.directory, 'subspiders', self.name)
        Utils.__init__(self, self.spider.crawler, *args, directory=self.directory, **kwargs)

        self.enabled = self.get_attribute('enabled')
        self.linker = self.get_attribute('linker')
        self.regex = self.get_attribute('regex')
        self.interval = self.get_attribute('interval')
        if isinstance(self.interval, (str, int)):
            self.interval = Interval(self.interval)

        self.subspiders = {}
        for _name, _subspider_cls in self.get_attribute('subspiders_cls').items():
            self.subspiders[_name] = init_subspiders(_subspider_cls, self.crawler, self.spider, self.name + '.' + _name, *args, **kwargs)
        self.subspiders = self.subspiders.items()

        self._state = STOP if self.enabled else DISABLED
        self._index_status = Index(self.spider.crawler, directory=self.directory, name=self.name + '.status', columns=['status', 'url', 'args', 'kwargs'])
        self._index_items = Index(self.spider.crawler, directory=self.directory, name=self.name + '.items', columns=['url', 'pipeline'])

        self.logger.debug('{:_<18} : OK'.format('Initialisation'))

    @classmethod
    def from_spider(cls, crawler, spider, *args, **kwargs):
        step = cls(crawler, spider, *args, **kwargs)
        step.spider.crawler.signals.connect(step.open, signal=scrapy.signals.spider_opened)
        step.spider.crawler.signals.connect(step.close, signal=scrapy.signals.spider_closed)
        return step

    def __str__(self):
        return self.infos.__str__()

    def __copy__(self):
        return self.__class__(self)
    copy = __copy__

    # ####################################################### #

    @staticmethod
    def possible_attributes():
        res = super(SubSpider, SubSpider).possible_attributes()
        res.update([
            Attribute('enabled', bool, True),
            Attribute('linker', bool, True),
            Attribute('regex', str, ''),
            Attribute('interval', (Interval, str, int), 0),
            Attribute('subspiders_cls', dict, {})
            ])
        return res

    @staticmethod
    def possible_functions():
        res = super(SubSpider, SubSpider).possible_functions()
        res.update([
            Function('start_links', (type(None), Iterable, str, URL, Link), []),
            Function('enqueue_request', (type(None), bool), False),
            Function('process_request', (type(None), Request), None),
            Function('process_response', (type(None), Response), None),
            Function('process_input', (type(None), object), None),
            Function('parse', (type(None), Iterable, Item, URL, Link, Interval), []),
            Function('process_output', (type(None), Iterable, Item, URL, Link), [])
            ])
        return res

    @property
    def infos(self):
        infos = super().infos
        infos['enabled'] = self.enabled
        infos['linker'] = self.linker
        infos['regex'] = self.regex
        infos['interval'] = (self.interval, str(self.interval))
        infos['index'] = self._index_status.infos
        infos['subspiders'] = {_name: _step.infos for _name, _step in self.subspiders}
        return infos

    # ####################################################### #

    def open(self, *args, **kwargs):
        self.logger.debug('{:_<18}'.format('Open'))
        Utils.open(self)

        if self._state == STOP:
            self._index_status.open()
            self._index_items.open()
            self._state = START
            self.logger.info('{:_<18} : OK   ITEMS = {:5} STATUS = {}'.format('Open', self._index_items.length, json.dumps(self._index_status.counts, indent=None, sort_keys=False)))

        elif self._state == START:
            self.logger.error('{:_<18} : FAIL !'.format('Open'))
            raise RuntimeError("%s already running !" % self.name)
        else:
            self.logger.info('{:_<18} : NO   [{}]'.format('Open', 'DISABLED'))

    def close(self, *args, **kwargs):
        self.logger.debug('{:_<18}'.format('Close'))
        Utils.close(self)

        if self._state == START:
            self._index_status.close()
            self._index_items.close()
            self._state = STOP
            self.logger.info('{:_<18} : OK   ITEMS = {:5} STATUS = {}'.format('Close', self._index_items.length, json.dumps(self._index_status.counts, indent=None, sort_keys=False)))

        elif self._state == STOP:
            self.logger.error('{:_<18} : FAIL !'.format('Close'))
            raise RuntimeError("%s not running !" % self.name)
        else:
            self.logger.info('{:_<18} : NO   [{}]'.format('Close', 'DISABLED'))

    # ####################################################### #
    # ####################################################### #

    @classmethod
    def handles(cls, url):
        if cls.match(url):
            return any(subspider_cls.handles(cls.next(url)) for _, subspider_cls in cls.subspiders_cls.items())
        return False

    @classmethod
    def match(cls, url):
        return url.match(cls.regex) if cls.enabled else False

    @classmethod
    def next(cls, url):
        return url.next(cls.regex) if cls.enabled else URL('')

    # ####################################################### #
    # ####################################################### #

    def start_links_(self):

        def format_links(links):
            if isinstance(links, (str, URL)):
                links = Link.create(links)
            elif isinstance(links, Link):
                pass
            elif isinstance(links, Iterable):
                links = [format_links(link) for link in links]
            elif links is None:
                links = []
            else:
                self.logger.error('{:_<18} : SKIP'.format('Invalid ['+links.__class__.__name__+']'))
                links = []
            return links

        yield from format_links(self.call_function('start_links', []))

        for _, _subspider in self.subspiders:
            yield from _subspider.start_links_()

    # ####################################################### #

    def enqueue_request_(self, request, url, *args, **kwargs):
        self.logger.debug('{:_<18} :      {} {}'.format('Enqueue Request', url.path, url.params))

        enqueue = True
        if self.match(url):
            url = self.next(url)

            try:
                enqueue = self.call_function('enqueue_request', True, request, url, *args, **kwargs)
                if not enqueue:
                    raise IgnoreRequest
                self.logger.debug('{:_<18} : OK   {} {}'.format('Enqueue Request', url.path, url.params))
            except IgnoreRequest:
                self.logger.debug('{:_<18} : DROP {} {}'.format('Enqueue Request', url.path, url.params))
                raise IgnoreRequest

            for _, _subspider in self.subspiders:
                enqueue = enqueue and _subspider.enqueue_request_(request, url, *args, **kwargs)
        else:
            self.logger.debug('{:_<18} : SKIP {} {}'.format('Enqueue Request', url.path, url.params))

        return enqueue

    # ####################################################### #

    def process_request_(self, request, url, *args, **kwargs):
        self.logger.debug('{:_<18} :      {} {}'.format('Process Request', url.path, url.params))

        if self.match(url):
            url = self.next(url)

            try:
                request = self.call_function('process_request', request, request, url, *args, **kwargs)
                if request is None:
                    raise IgnoreRequest
                self.logger.debug('{:_<18} : OK   {} {}'.format('Process Request', url.path, url.params))
            except IgnoreRequest:
                self.logger.debug('{:_<18} : DROP {} {}'.format('Process Request', url.path, url.params))
                raise IgnoreRequest

            for _, _subspider in self.subspiders:
                request = _subspider.process_request_(request, url, *args, **kwargs)
        else:
            self.logger.debug('{:_<18} : SKIP {} {}'.format('Process Request', url.path, url.params))

        return request

    # ####################################################### #

    def process_response_(self, response, url, *args, **kwargs):
        self.logger.debug('{:_<18} :      {} {}'.format('Process Response', url.path, url.params))

        if self.match(url):
            url = self.next(url)

            try:
                response = self.call_function('process_response', response, response, url, *args, **kwargs)
                if response is None:
                    raise IgnoreResponse
                self.logger.debug('{:_<18} : OK   {} {}'.format('Process Response', url.path, url.params))
            except IgnoreResponse:
                self.logger.debug('{:_<18} : DROP {} {}'.format('Process Response', url.path, url.params))
                raise IgnoreResponse

            for _, _subspider in self.subspiders:
                response = _subspider.process_response_(response, url, *args, **kwargs)

        else:
            self.logger.debug('{:_<18} : SKIP {} {}'.format('Process Response', url.path, url.params))

        return response

    # ####################################################### #

    def parse_(self, response, url, *args, **kwargs):
        self.logger.debug('{:_<18} :      {} {}'.format('Parse', url.path, url.params))

        status = '!'
        if self.match(url):
            url = self.next(url)

            response = self.call_function('process_input', response, response, url, *args, **kwargs)
            if response is not None:
                if len(url.remaining) == 0:
                    status = False
                    interval = self.interval
                    results = self.call_function('parse', [], response, url, *args, **kwargs)
                    for result in self.process_results_(results, url, *args, **kwargs):
                        status = True
                        if isinstance(result, Item):
                            self._index_items.add(url=url, pipeline=result['pipeline'])
                            self.logger.info('{:_<18} : OK   {} {} --> \'{}\''.format('Parse', url.path, url.params, result['pipeline']))
                        elif isinstance(result, Interval):
                            interval = result
                            continue
                        yield result

                    if interval > 0 and self.crawler.settings.get('COMMAND') in ['crawl', 'runspider']:
                        yield Link(url, timestamp=time.time()+interval, cb_kwargs=kwargs.update(interval.cb_kwargs))
                        self.logger.debug('{:_<18} : OK   {} {} --> {}'.format('Interval', url.path, url.params, interval))
                    else:
                        self.logger.debug('{:_<18} : NO   {} {}'.format('Interval', url.path, url.params))

                    if status is False:
                        self.logger.info('{:_<18} : DROP {} {}'.format('Parse', url.path, url.params))
                    else:
                        self.spider.crawler.stats.inc_value('subspiders/'+self.name)
                else:
                    status = '_'
                    for _, _subspider in self.subspiders:
                        results = _subspider.parse_(response, url, *args, **kwargs) or []
                        yield from self.process_results_(results, url, *args, **kwargs)
        else:
            self.logger.debug('{:_<18} : SKIP {} {}'.format('Parse', url.path, url.params))
            yield

        self._index_status.add(status=status, url=url, args=str(args), kwargs=str(kwargs))

    # ####################################################### #

    def process_results_(self, results, url, *args, item=None, **kwargs):

        def format_results(res):
            if isinstance(res, (Item, URL, Link)):
                return [res]
            if isinstance(res, Iterable):
                return res
            if res is None:
                return []
            self.logger.error('{:_<18} : SKIP {} {}'.format('Invalid ['+res.__class__.__name__+']', url.path, url.params))
            return []

        self.logger.debug('{:_<18} :      {} {}'.format('Process Results', url.path, url.params))

        for result in filter(None, format_results(results)):
            if isinstance(result, Item):
                if result != item:
                    item = result
                    results = self.call_function('process_output', item, url, item, *args, **kwargs)
                    yield from self.process_results_(results, url, *args, item=item, **kwargs)
                else:
                    yield item
            elif isinstance(result, (URL, Link)):
                if self.linker:
                    yield result
            elif isinstance(result, Interval):
                yield result
            else:
                yield from self.process_results_(result, url, *args, item=item, **kwargs)
        yield from []

        self.logger.debug('{:_<18} : OK   {} {}'.format('Process Results', url.path, url.params))

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
