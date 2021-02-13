""" Ratpy Scheduler Queues module """

import time

from ratpy.utils import Logger

# ############################################################### #
# ############################################################### #


class RatpyListQueue(Logger):

    """ Ratpy List Queue class """

    # ####################################################### #
    # ####################################################### #

    name = 'queue.list'

    _list = None
    _total = None

    # ####################################################### #

    def __init__(self, crawler, work_dir, log_dir):

        Logger.__init__(self, crawler, log_dir=log_dir)

    # ####################################################### #

    @property
    def infos(self):
        infos = super().infos
        infos['size'] = len(self)
        return infos

    # ####################################################### #

    def open(self):
        self._list = []
        self._total = 0

    def close(self):
        for _ in self._list:
            del self._list[0]
            self._total -= 1

    # ####################################################### #

    def empty(self):
        return self._total == 0

    def __len__(self):
        return self._total

    def __del__(self):
        self.close()

    # ####################################################### #
    # ####################################################### #

    def push(self, item, timestamp):
        x = (item, timestamp)
        self._list.append(x)
        self._list.sort(key=lambda elem: elem[1])
        self._total += 1

    def pop(self):
        if self._total and self._list[0][1] <= time.time():
            self._total -= 1
            return self._list.pop(0)[0]
        return None

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
