""" Ratpy Item Pipelines module """

import scrapy

from ratpy.utils import Logger, monitored

# ############################################################### #
# ############################################################### #


@monitored
class RatpyItemPipeline(Logger):

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
        Logger.__init__(self, self.crawler, directory=self.directory)

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls(crawler)
        crawler.signals.connect(pipeline.open,  signal=scrapy.signals.spider_opened)
        crawler.signals.connect(pipeline.close, signal=scrapy.signals.spider_closed)
        return pipeline

    # ####################################################### #

    def open(self, spider, *args, **kwargs):
        self.logger.debug(action='Open')

        if spider.name not in self.spiders:
            self.spiders[spider.name] = spider
            self.logger.info(action='Open', status='OK', message='[{}]'.format(spider.name))
        else:
            self.logger.error(action='Open', status='FAIL', message='[{}]'.format(spider.name))
            raise RuntimeError("%s pipeline already running !" % spider.name)

    def close(self, spider, *args, **kwargs):
        self.logger.debug(action='Close')

        if spider.name in self.spiders:
            del self.spiders[spider.name]
            self.logger.info(action='Close', status='OK', message='[{}]'.format(spider.name))
        else:
            self.logger.error(action='Close', status='FAIL', message='[{}]'.format(spider.name))
            raise RuntimeError("%s pipeline not running !" % spider.name)

    # ####################################################### #

    def process_item(self, item, spider):
        self.logger.debug(action='Process Item', status='OK', message='[{}]'.format(item['pipeline']))
        return item

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
