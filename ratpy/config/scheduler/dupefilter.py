"""Ratpy Dupefilter module """

import os

from ratpy.utils import Logger
from ratpy.utils.path import work_directory, log_directory, create_file
from ratpy.http.request.fingerprint import request_fingerprint

# ############################################################### #
# ############################################################### #


class RatpyDupefilter(Logger):

    """ Ratpy Dupefilter class """

    # ####################################################### #
    # ####################################################### #

    name = 'ratpy.dupefilter'

    crawler = None
    spider = None

    work_path = None

    fingerprints = None

    # ####################################################### #

    def __init__(self, crawler):

        self.crawler = crawler

        self.fingerprints = set()

        Logger.__init__(self, self.crawler, log_dir=os.path.join(log_directory(crawler.settings), 'scheduler'))

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    # ####################################################### #

    def open(self, spider):
        self.logger.debug('{:_<18}'.format('Open'))

        self.spider = spider

        self.work_path = os.path.join(work_directory(self.crawler.settings), 'scheduler', 'requests.fingerprints')
        create_file(self.work_path, 'w+', '')

        with open(self.work_path, 'r+') as file:
            self.fingerprints.update(x.rstrip() for x in file)

        self.logger.info('{:_<18} : OK   [{}] Requests : {}'.format('Open', self.spider.name, len(self)))

    def close(self, reason):
        self.logger.debug('{:_<18}'.format('Close'))

        if self.work_path and self.crawler.settings.get('WORK_ON_DISK', False):
            with open(self.work_path, 'w+') as file:
                for fp in self.fingerprints:
                    file.write(fp + '\n')

        self.logger.info('{:_<18} : OK   [{}] Requests : {}'.format('Close', self.spider.name, len(self)))

    # ####################################################### #

    def __len__(self):
        return len(self.fingerprints)

    @property
    def infos(self):
        infos = super().infos
        infos['work_path'] = self.work_path
        infos['filtered'] = len(self)
        return infos

    # ####################################################### #
    # ####################################################### #

    def seen(self, request):

        self.crawler.stats.inc_value('dupefilter/inputs', spider=self.spider)

        _fp = RatpyDupefilter.fingerprint(request)
        if _fp in self.fingerprints:
            self.logger.debug('{:_<18} : OK   [{}]'.format('Filtered', request.url))
            return True

        self.fingerprints.add(_fp)

        self.crawler.stats.inc_value('dupefilter/outputs', spider=self.spider)
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
