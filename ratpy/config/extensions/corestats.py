""" Ratpy Core Stats Extension module """

from datetime import datetime

from scrapy import signals
from scrapy.exceptions import NotConfigured

from ratpy.utils import Logger

# ############################################################### #
# ############################################################### #


class CoreStats(Logger):

    """ Ratpy Core Stats Extension class """

    # ####################################################### #
    # ####################################################### #

    name = 'ratpy.extensions.corestat'

    directory = 'extensions'
    crawler = None
    
    time_begin = None
    time_end = None
    time_total = None

    # ####################################################### #

    def __init__(self, crawler):

        if not crawler.settings.getbool('CORE_STATS_ENABLED'):
            raise NotConfigured

        self.crawler = crawler
        Logger.__init__(self, self.crawler, directory=self.directory)

    @classmethod
    def from_crawler(cls, crawler):
        extension = cls(crawler)
        crawler.signals.connect(extension.open, signal=signals.spider_opened)
        crawler.signals.connect(extension.close, signal=signals.spider_closed)
        crawler.signals.connect(extension.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(extension.item_dropped, signal=signals.item_dropped)
        crawler.signals.connect(extension.response_received, signal=signals.response_received)
        return extension

    # ####################################################### #

    def open(self, spider):
        self.logger.debug('{:_<18}'.format('Open'))

        self.time_begin = datetime.utcnow()
        self.crawler.stats.set_value('time_begin', self.time_begin)

        self.logger.info('{:_<18} : OK'.format('Open'))

    def close(self, spider, reason):
        self.logger.debug('{:_<18}'.format('Close'))

        self.time_end = datetime.utcnow()
        self.time_total = self.time_end - self.time_begin
        self.crawler.stats.set_value('time_total_seconds', self.time_total.total_seconds())
        self.crawler.stats.set_value('time_end', self.time_end)
        self.crawler.stats.set_value('end_reason', reason)

        self.logger.info('{:_<18} : OK'.format('Close'))

    # ####################################################### #
    # ####################################################### #

    def item_scraped(self, item, spider):
        self.crawler.stats.inc_value('item_scraped_count')

    def item_dropped(self, item, spider, exception):
        reason = exception.__class__.__name__
        self.crawler.stats.inc_value('item_dropped_count')
        self.crawler.stats.inc_value('item_dropped_reasons_count/%s' % reason)

    def response_received(self, spider):
        self.crawler.stats.inc_value('response_received_count')

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
