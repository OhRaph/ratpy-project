""" Ratpy Middlewares module """

import os
import scrapy

from ratpy.utils import Logger, log_directory
from ratpy import URL, Item

from ratpy.http.request import Request, IgnoreRequest
from ratpy.http.response import Response, IgnoreResponse

# ############################################################### #
# ############################################################### #


class RatpyDownloaderMiddleware(Logger):

    """ Ratpy Downloader Middleware class """

    # ####################################################### #
    # ####################################################### #

    name = 'ratpy.middleware.downloader'

    crawler = None

    spiders = None

    # ####################################################### #

    def __init__(self, crawler):

        self.crawler = crawler

        self.spiders = {}

        Logger.__init__(self, self.crawler, log_dir=os.path.join(log_directory(crawler.settings), 'middlewares'))

        self.logger.debug('{:_<18} : OK'.format('Initialisation'))

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls(crawler)
        crawler.signals.connect(middleware.open,  signal=scrapy.signals.spider_opened)
        crawler.signals.connect(middleware.close, signal=scrapy.signals.spider_closed)
        return middleware

    # ####################################################### #

    def open(self, spider):
        self.logger.debug('{:_<18}'.format('Open'))

        if spider.name not in self.spiders:
            self.spiders[spider.name] = spider
            self.logger.info('{:_<18} : OK   [{}]'.format('Open', spider.name))
        else:
            self.logger.error('{:_<18} : FAIL !'.format('Open'))
            raise RuntimeError("%s middleware already running !" % spider.name)

    def close(self, spider):
        self.logger.debug('{:_<18}'.format('Close'))

        if spider.name in self.spiders:
            del self.spiders[spider.name]
            self.logger.info('{:_<18} : OK   [{}]'.format('Close', spider.name))
        else:
            self.logger.error('{:_<18} : FAIL !'.format('Close'))
            raise RuntimeError("%s middleware not running !" % spider.name)

    # ####################################################### #

    def process_request(self, request, spider):
        self.logger.debug('{:_<18} :      \'{}\''.format('Process Request', request.url))

        if spider.name not in self.spiders:
            raise RuntimeError("%s middleware not running !" % spider.name)
        request.__class__ = Request

        url = URL(request.url)
        try:
            request = spider.subspiders.process_request_(request, url, **request.cb_kwargs)
            if request is None:
                raise IgnoreRequest
        except IgnoreRequest:
            self.logger.debug('{:_<18} : DROP \'{}\''.format('Process Request', request.url))
            raise scrapy.exceptions.IgnoreRequest
        else:
            if url == URL(request.url):
                self.logger.debug('{:_<18} : OK   \'{}\''.format('Process Request', request.url))
                request = None
            else:
                self.logger.debug('{:_<18} : OK   \'{}\' --> \'{}\''.format('Process Request', url, request.url))

        return request

    def process_response(self, request, response, spider):
        self.logger.debug('{:_<18} :      \'{}\''.format('Process Response', request.url))

        if spider.name not in self.spiders:
            raise RuntimeError("%s middleware not running !" % spider.name)
        request.__class__ = Request
        response.__class__ = Response

        url = URL(response.url)
        try:
            response = spider.subspiders.process_response_(response, url, **request.cb_kwargs)
            if response is None:
                raise IgnoreResponse
        except IgnoreResponse:
            self.logger.debug('{:_<18} : DROP \'{}\''.format('Process Response', request.url))
            raise scrapy.exceptions.IgnoreRequest
        else:
            self.logger.debug('{:_<18} : OK   \'{}\''.format('Process Response', request.url))

        return response

    def process_exception(self, request, exception, spider):
        self.logger.debug('{:_<18} : OK   [{}] \'{}\''.format('Process Exception', exception, request.url))

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #


class RatpySpiderMiddleware(Logger):

    """ Ratpy Spider Middleware class """

    # ####################################################### #
    # ####################################################### #

    name = 'ratpy.middleware.spider'

    crawler = None

    spiders = None

    # ####################################################### #

    def __init__(self, crawler):

        self.crawler = crawler

        self.spiders = {}

        Logger.__init__(self, self.crawler, log_dir=os.path.join(log_directory(crawler.settings), 'middlewares'))

        self.logger.debug('{:_<18} : OK'.format('Initialisation'))

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls(crawler)
        crawler.signals.connect(middleware.open,  signal=scrapy.signals.spider_opened)
        crawler.signals.connect(middleware.close, signal=scrapy.signals.spider_closed)
        return middleware

    # ####################################################### #

    def open(self, spider):
        self.logger.debug('{:_<18}'.format('Open'))

        if spider.name not in self.spiders:
            self.spiders[spider.name] = spider
            self.logger.info('{:_<18} : OK   [{}]'.format('Open', spider.name))
        else:
            self.logger.error('{:_<18} : FAIL !'.format('Open'))
            raise RuntimeError("%s middleware already running !" % spider.name)

    def close(self, spider):
        self.logger.debug('{:_<18}'.format('Close'))

        if spider.name in self.spiders:
            del self.spiders[spider.name]
            self.logger.info('{:_<18} : OK   [{}]'.format('Close', spider.name))
        else:
            self.logger.error('{:_<18} : FAIL !'.format('Close'))
            raise RuntimeError("%s middleware not running !" % spider.name)

    # ####################################################### #

    def process_spider_input(self, response, spider):

        if spider.name not in self.spiders:
            raise RuntimeError("%s middleware not running !" % spider.name)

        spider.crawler.stats.inc_value(spider.name + '/inputs')
        self.logger.debug('{:_<18} : OK   [{: <8}] \'{}\''.format('Process Input', 'Response', response.url))

    def process_spider_output(self, response, result, spider):

        if spider.name not in self.spiders:
            raise RuntimeError("%s middleware not running !" % spider.name)

        for hit in result:
            spider.crawler.stats.inc_value(spider.name + '/outputs')
            if isinstance(hit, Item):
                spider.crawler.stats.inc_value(spider.name+'/outputs/items')
                self.logger.debug('{:_<18} : OK   [{: <8}]'.format('Process Output', 'Item'))
            elif isinstance(hit, Request):
                spider.crawler.stats.inc_value(spider.name+'/outputs/requests')
                self.logger.debug('{:_<18} : OK   [{: <8}] \'{}\''.format('Process Output', 'Request', hit.url))
            yield hit

    def process_spider_exception(self, response, exception, spider):
        self.logger.debug('{:_<18} : OK   [{}] \'{}\''.format('Process Exception', exception, response.url))

    @staticmethod
    def process_start_requests(start_requests, spider):
        yield from start_requests

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
