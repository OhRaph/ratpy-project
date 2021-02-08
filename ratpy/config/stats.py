""" Ratpy Stats Collector module """

import json
import os

from ratpy.utils import Logger
from ratpy.utils.path import work_directory, log_directory, create_directory, create_file

# ############################################################### #
# ############################################################### #

DUMP_BEGIN = object()
DUMP_END = object()


class StatsCollector(Logger):

    """ Ratpy Stats Collector class """

    # ####################################################### #
    # ####################################################### #

    name = 'ratpy.stats'

    crawler = None

    work_dir = None
    work_path = None

    _dump = False
    _store = False

    _stats = None
    _previous_stats = None

    # ####################################################### #

    def __init__(self, crawler):

        self.crawler = crawler

        self.work_dir = os.path.join(work_directory(crawler.settings), 'stats')
        create_directory(self.work_dir)

        self._dump = self.crawler.settings.getbool('STATS_DUMP')
        self._store = self.crawler.settings.getbool('STATS_STORE')

        self._stats = {}
        self._previous_stats = {}

        Logger.__init__(self, self.crawler, log_dir=log_directory(crawler.settings))

    # ####################################################### #

    def open_spider(self, spider):
        if self._store and self.crawler.settings.get('WORK_ON_DISK', False):
            self.work_path = os.path.join(self.work_dir, spider.name+'.stats')
            create_file(self.work_path, 'w+', json.dumps({}, indent=4, sort_keys=True))
            with open(self.work_path, 'r') as file:
                self._previous_stats = json.loads(file.read())
        if self._dump:
            self.logger.info("Dumping Ratpy stats:\n" + self._to_dump_stats(DUMP_BEGIN))

    def close_spider(self, spider, reason):
        if self._store and self.crawler.settings.get('WORK_ON_DISK', False):
            with open(self.work_path, 'w+') as file:
                file.write(json.dumps(self._to_store_stats(), indent=4, sort_keys=True, default=str))
        if self._dump:
            self.logger.info("Dumping Ratpy stats:\n" + self._to_dump_stats(DUMP_END))

    # ####################################################### #
    # ####################################################### #

    def get_value(self, key, default=None, spider=None):
        return self._stats.get(key, default)

    def get_stats(self, spider=None):
        return self._stats

    def set_value(self, key, value, spider=None):
        self._stats[key] = value

    def set_stats(self, stats, spider=None):
        self._stats = stats

    def inc_value(self, key, count=1, start=0, spider=None):
        self._stats[key] = self._stats.setdefault(key, start) + count

    def max_value(self, key, value, spider=None):
        self._stats[key] = max(self._stats.setdefault(key, value), value)

    def min_value(self, key, value, spider=None):
        self._stats[key] = min(self._stats.setdefault(key, value), value)

    def clear_stats(self, spider=None):
        self._stats.clear()

    # ####################################################### #
    # ####################################################### #

    def _to_store_stats(self):

        res = self._previous_stats.copy()
        for _key, _value in self._stats.items():
            if isinstance(_value, int):
                res[_key] = _value + self._previous_stats.get(_key, 0)
            else:
                res[_key] = _value
        return res

    def _to_dump_stats(self, dump_state):

        tmp1 = self._previous_stats.copy()
        for _key, _value in self._stats.items():
            if isinstance(_value, int):
                tmp1[_key] = _value + self._previous_stats.get(_key, 0)
            else:
                tmp1[_key] = None

        tmp2 = self._stats.copy()
        for _key, _value in self._previous_stats.items():
            default_value = None if dump_state == DUMP_BEGIN and not isinstance(_value, int) else 0
            tmp2[_key] = self._stats.get(_key, default_value)

        res = '{\n'
        for _key in sorted(tmp1):
            if isinstance(tmp1[_key], int):
                res += '  {:_<70}: {: >12} [+{: >12}]\n'.format(_key, str(tmp1[_key]), str(tmp2[_key]))
            else:
                res += '  {:_<70}: {: >28}\n'.format(_key, str(tmp2[_key]))
        res += '}'

        return res

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
