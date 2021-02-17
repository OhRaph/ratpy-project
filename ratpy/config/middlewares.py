""" Ratpy Middlewares module """

import scrapy

from ratpy.utils import Logger, monitored
from ratpy import URL, Item

from ratpy.http.request import Request, IgnoreRequest
from ratpy.http.response import Response, IgnoreResponse

# ############################################################### #
# ############################################################### #


@monitored
class RatpyDownloaderMiddleware(Logger):

    """ Ratpy Downloader Middleware class """

    # ####################################################### #
    # ####################################################### #

    name = 'ratpy.middleware.downloader'

    directory = 'middlewares'
    crawler = None
    spiders = None

    # ####################################################### #

    def __init__(self, crawler):

        self.crawler = crawler
        self.spiders = {}
        Logger.__init__(self, self.crawler, directory=self.directory)

        self.logger.debug(action='Initialisation', status='OK')

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls(crawler)
        crawler.signals.connect(middleware.open,  signal=scrapy.signals.spider_opened)
        crawler.signals.connect(middleware.close, signal=scrapy.signals.spider_closed)
        return middleware

    # ####################################################### #

    def open(self, spider, *args, **kwargs):
        self.logger.debug(action='Open')

        if spider.name not in self.spiders:
            self.spiders[spider.name] = spider
            self.logger.info(action='Open', status='OK', message='[{}]'.format(spider.name))
        else:
            self.logger.error(action='Open', status='FAIL', message='[{}]'.format(spider.name))
            raise RuntimeError("{} middleware already running !".format(spider.name))

    def close(self, spider, *args, **kwargs):
        self.logger.debug(action='Close')

        if spider.name in self.spiders:
            del self.spiders[spider.name]
            self.logger.info(action='Close', status='OK', message='[{}]'.format(spider.name))
        else:
            self.logger.error(action='Close', status='FAIL', message='[{}]'.format(spider.name))
            raise RuntimeError("{} middleware not running !".format(spider.name))

    # ####################################################### #

    def process_request(self, request, spider):
        self.logger.debug(action='Process Request', message='{}'.format(request.url))

        if spider.name not in self.spiders:
            self.logger.error(action='Process Request', status='FAIL', message='[{}]'.format(spider.name))
            raise RuntimeError('{} middleware not running !'.format(spider.name))
        request.__class__ = Request

        url = URL(request.url)
        try:
            request = spider.subspiders.process_request_(request, url, **request.cb_kwargs)
            if request is None:
                raise IgnoreRequest
        except IgnoreRequest:
            self.logger.debug(action='Process Request', status='DROP', message='{}'.format(request.url))
            raise scrapy.exceptions.IgnoreRequest
        else:
            if url == URL(request.url):
                self.logger.debug(action='Process Request', status='OK', message='{}'.format(request.url))
                request = None
            else:
                self.logger.debug(action='Process Request', status='DROP', message='{} --> {}'.format(url, request.url))

        return request

    def process_response(self, request, response, spider):
        self.logger.debug(action='Process Response', message='{}'.format(request.url))

        if spider.name not in self.spiders:
            self.logger.error(action='Process Response', status='FAIL', message='[{}]'.format(spider.name))
            raise RuntimeError('{} middleware not running !'.format(spider.name))
        request.__class__ = Request
        response.__class__ = Response

        url = URL(response.url)
        try:
            response = spider.subspiders.process_response_(response, url, **request.cb_kwargs)
            if response is None:
                raise IgnoreResponse
        except IgnoreResponse:
            self.logger.debug(action='Process Response', status='DROP', message='{}'.format(request.url))
            raise scrapy.exceptions.IgnoreRequest
        else:
            self.logger.debug(action='Process Response', status='OK', message='{}'.format(request.url))

        return response

    def process_exception(self, request, exception, spider):
        self.logger.debug(action='Process Exception', status='OK', message='[{}] {}'.format(exception, request.url))

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #


@monitored
class RatpySpiderMiddleware(Logger):

    """ Ratpy Spider Middleware class """

    # ####################################################### #
    # ####################################################### #

    name = 'ratpy.middleware.spider'

    directory = 'middlewares'
    crawler = None
    spiders = None

    # ####################################################### #

    def __init__(self, crawler):

        self.crawler = crawler
        self.spiders = {}
        Logger.__init__(self, self.crawler, directory=self.directory)

        self.logger.debug(action='Initialisation')

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls(crawler)
        crawler.signals.connect(middleware.open,  signal=scrapy.signals.spider_opened)
        crawler.signals.connect(middleware.close, signal=scrapy.signals.spider_closed)
        return middleware

    # ####################################################### #

    def open(self, spider, *args, **kwargs):
        self.logger.debug(action='Open')

        if spider.name not in self.spiders:
            self.spiders[spider.name] = spider
            self.logger.info(action='Open', status='OK', message='[{}]'.format(spider.name))
        else:
            self.logger.error(action='Open', status='FAIL', message='[{}]'.format(spider.name))
            raise RuntimeError('{} middleware already running !'.format(spider.name))

    def close(self, spider, *args, **kwargs):
        self.logger.debug(action='Close')

        if spider.name in self.spiders:
            del self.spiders[spider.name]
            self.logger.info(action='Close', status='OK', message='[{}]'.format(spider.name))
        else:
            self.logger.error(action='Close', status='FAIL', message='[{}]'.format(spider.name))
            raise RuntimeError('{} middleware not running !'.format(spider.name))

    # ####################################################### #

    def process_spider_input(self, response, spider):

        if spider.name not in self.spiders:
            self.logger.error(action='Process Input', status='FAIL', message='[{}]'.format(spider.name))
            raise RuntimeError("{} middleware not running !".format(spider.name))

        spider.crawler.stats.inc_value(spider.name + '/inputs')
        self.logger.debug(action='Process Input', status='OK', message='[{: <8}] {}'.format('Response', response.url))

    def process_spider_output(self, response, result, spider):

        if spider.name not in self.spiders:
            self.logger.error(action='Process Output', status='FAIL', message='[{}]'.format(spider.name))
            raise RuntimeError("{} middleware not running !".format(spider.name))

        for hit in result:
            spider.crawler.stats.inc_value(spider.name + '/outputs')
            if isinstance(hit, Item):
                spider.crawler.stats.inc_value(spider.name+'/outputs/items')
                self.logger.debug(action='Process Output', status='OK', message='[{: <8}]'.format('Item'))
            elif isinstance(hit, Request):
                spider.crawler.stats.inc_value(spider.name+'/outputs/requests')
                self.logger.debug(action='Process Output', status='OK', message='[{: <8}] {}'.format('Item', hit.url))
            yield hit

    def process_spider_exception(self, response, exception, spider):
        self.logger.debug(action='Process Exception', status='OK', message='[{}] {}'.format(exception, response.url))

    def process_start_requests(self, start_requests, spider):
        yield from start_requests

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
