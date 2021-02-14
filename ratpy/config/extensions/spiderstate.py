""" Ratpy Spider State Extension module """

import json
import os

from scrapy import signals
from scrapy.exceptions import NotConfigured

from ratpy.utils import Logger
from ratpy.utils.path import work_directory, create_file

# ############################################################### #
# ############################################################### #


class SpiderState(Logger):

    """ Ratpy Spider State Extension class """

    # ####################################################### #
    # ####################################################### #

    name = 'ratpy.extensions.spiderstate'

    directory = 'extensions'
    crawler = None

    work_file = None

    # ####################################################### #

    def __init__(self, crawler):

        if not crawler.settings.getbool('SPIDER_STATE_ENABLED'):
            raise NotConfigured

        self.crawler = crawler
        Logger.__init__(self, self.crawler, directory=self.directory)

    @classmethod
    def from_crawler(cls, crawler):
        extension = cls(crawler)
        crawler.signals.connect(extension.open, signal=signals.spider_opened)
        crawler.signals.connect(extension.close, signal=signals.spider_closed)
        return extension

    # ####################################################### #

    def open(self, spider):
        self.logger.debug('{:_<18}'.format('Open'))

        if self.crawler.settings.get('WORK_ON_DISK', False):
            self.work_file = os.path.join(work_directory(self.crawler.settings), self.directory, self.name, spider.name+'.state')
            create_file(self.work_file, 'w+', json.dumps({}, indent=4, sort_keys=True))
            with open(self.work_file, 'r') as file:
                spider.state = json.loads(file.read())

        self.logger.info('{:_<18} : OK'.format('Open'))

    def close(self, spider):
        self.logger.debug('{:_<18}'.format('Close'))

        if self.crawler.settings.get('WORK_ON_DISK', False):
            with open(self.work_file, 'w+') as file:
                file.write(json.dumps(spider.state, indent=4, sort_keys=False))
                file.close()

        self.logger.info('{:_<18} : OK'.format('Close'))

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
