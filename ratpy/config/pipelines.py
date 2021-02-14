""" Ratpy Item Pipelines module """

import scrapy

from ratpy.utils import Logger, Monitor

# ############################################################### #
# ############################################################### #


class RatpyItemPipeline(Logger, Monitor):

    """ Ratpy Item Pipeline class """

    # ####################################################### #
    # ####################################################### #

    name = 'ratpy.pipeline'

    directory = 'pipelines'
    crawler = None
    spiders = None

    # ####################################################### #

    def __init__(self, crawler):

        self.crawler = crawler
        self.spiders = {}
        Monitor.__init__(self, self.crawler, directory=self.directory)
        Logger.__init__(self, self.crawler, directory=self.directory)

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls(crawler)
        crawler.signals.connect(pipeline.open,  signal=scrapy.signals.spider_opened)
        crawler.signals.connect(pipeline.close, signal=scrapy.signals.spider_closed)
        return pipeline

    # ####################################################### #

    def open(self, spider):
        self.logger.debug('{:_<18}'.format('Open'))
        Monitor.open(self)

        if spider.name not in self.spiders:
            self.spiders[spider.name] = spider
            self.logger.info('{:_<18} : OK   [{}]'.format('Open', spider.name))
        else:
            self.logger.error('{:_<18} : FAIL !'.format('Open'))
            raise RuntimeError("%s pipeline already running !" % spider.name)

    def close(self, spider):
        self.logger.debug('{:_<18}'.format('Close'))
        Monitor.close(self)

        if spider.name in self.spiders:
            del self.spiders[spider.name]
            self.logger.info('{:_<18} : OK   [{}]'.format('Close', spider.name))
        else:
            self.logger.error('{:_<18} : FAIL !'.format('Close'))
            raise RuntimeError("%s pipeline not running !" % spider.name)

    # ####################################################### #

    def process_item(self, item, spider):
        return item

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
