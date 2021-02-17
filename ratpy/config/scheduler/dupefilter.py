"""Ratpy Dupefilter module """

import os

from ratpy.utils import Logger, monitored
from ratpy.utils.path import work_directory, create_file
from ratpy.http.request.fingerprint import request_fingerprint

# ############################################################### #
# ############################################################### #


@monitored
class RatpyDupefilter(Logger):

    """ Ratpy Dupefilter class """

    # ####################################################### #
    # ####################################################### #

    name = 'ratpy.dupefilter'

    directory = None
    crawler = None
    spider = None

    work_file = None

    fingerprints = None

    # ####################################################### #

    def __init__(self, crawler, directory):

        self.directory = os.path.join(directory, 'dupefilter')
        self.crawler = crawler
        Logger.__init__(self, self.crawler, directory=self.directory)

        self.work_file = os.path.join(work_directory(self.crawler.settings), self.directory, 'requests.fingerprints')
        self.fingerprints = set()

        self.logger.debug(action='Initialisation', status='OK')

    @classmethod
    def from_crawler(cls, crawler, directory):
        return cls(crawler, directory)

    # ####################################################### #

    def open(self, spider, *args, **kwargs):
        self.logger.debug(action='Open')

        self.spider = spider

        if self.crawler.settings.get('WORK_ON_DISK', False):
            create_file(self.work_file, 'w+', '')

            with open(self.work_file, 'r+') as file:
                self.fingerprints.update(x.rstrip() for x in file)

        self.logger.info(action='Open', status='OK', message='[{}] Requests : {}'.format(self.spider.name, len(self)))

    def close(self, reason, *args, **kwargs):
        self.logger.debug(action='Close')

        if self.crawler.settings.get('WORK_ON_DISK', False):
            with open(self.work_file, 'w+') as file:
                for fp in self.fingerprints:
                    file.write(fp + '\n')

        self.logger.info(action='Close', status='OK', message='[{}] Requests : {}'.format(self.spider.name, len(self)))

    # ####################################################### #

    def __len__(self):
        return len(self.fingerprints)

    @property
    def infos(self):
        infos = super().infos
        infos['work_file'] = self.work_file
        infos['filtered'] = len(self)
        return infos

    # ####################################################### #
    # ####################################################### #

    def seen(self, request):

        self.crawler.stats.inc_value('scheduler/dupefilter/inputs', spider=self.spider)

        _fp = RatpyDupefilter.fingerprint(request)
        if _fp in self.fingerprints:
            self.logger.debug(action='Filter', status='OK', message='[{}]'.format(request.url))
            return True

        self.fingerprints.add(_fp)

        self.crawler.stats.inc_value('scheduler/dupefilter/outputs', spider=self.spider)
        return False

    @staticmethod
    def fingerprint(request):
        return request_fingerprint(request)

    def log(self, request, spider):
        pass

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
