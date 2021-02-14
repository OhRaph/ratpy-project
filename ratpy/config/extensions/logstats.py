""" Ratpy Log Stats Extension module """

from twisted.internet import task

from scrapy import signals
from scrapy.exceptions import NotConfigured

from ratpy.utils import Logger

# ############################################################### #
# ############################################################### #


class LogStats(Logger):

    """ Ratpy Log Stats Extension class """

    # ####################################################### #
    # ####################################################### #

    name = 'ratpy.extensions.logstats'

    directory = 'extensions'
    crawler = None

    task = None

    interval = None
    multiplier = None

    pagesprev = None
    itemsprev = None

    # ####################################################### #

    def __init__(self, crawler, interval=60.0):

        if not crawler.settings.getbool('LOG_STATS_ENABLED'):
            raise NotConfigured

        self.crawler = crawler
        Logger.__init__(self, self.crawler, directory=self.directory)

        self.interval = interval
        self.multiplier = 60.0 / self.interval

    @classmethod
    def from_crawler(cls, crawler):
        interval = crawler.settings.getfloat('LOG_STATS_INTERVAL')
        if not interval or interval == -1:
            raise NotConfigured
        extension = cls(crawler, interval)
        crawler.signals.connect(extension.open, signal=signals.spider_opened)
        crawler.signals.connect(extension.close, signal=signals.spider_closed)
        return extension

    # ####################################################### #

    def open(self, spider):
        self.logger.debug('{:_<18}'.format('Open'))

        self.pagesprev = 0
        self.itemsprev = 0

        self.task = task.LoopingCall(self.log, spider)
        self.task.start(self.interval, now=False)

        self.logger.info('{:_<18} : OK'.format('Open'))

    def close(self, spider, reason):
        self.logger.debug('{:_<18}'.format('Close'))

        if self.task and self.task.running:
            self.task.stop()

        self.logger.info('{:_<18} : OK'.format('Close'))

    # ####################################################### #
    # ####################################################### #

    def log(self, spider):
        items = self.crawler.stats.get_value('item_scraped_count', 0)
        pages = self.crawler.stats.get_value('response_received_count', 0)
        irate = (items - self.itemsprev) * self.multiplier
        prate = (pages - self.pagesprev) * self.multiplier
        self.pagesprev, self.itemsprev = pages, items

        msg = "Crawled %(pages)d pages (at %(pagerate)d pages/min), scraped %(items)d items (at %(itemrate)d items/min)"
        log_args = {
            'pages': pages,
            'pagerate': prate,
            'items': items,
            'itemrate': irate
            }
        self.logger.info(msg, log_args)

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
