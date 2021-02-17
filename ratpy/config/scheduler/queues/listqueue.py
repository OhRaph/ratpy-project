""" Ratpy Scheduler Queues module """

import os
import time

from ratpy.utils import Logger, monitored

# ############################################################### #
# ############################################################### #


@monitored
class RatpyListQueue(Logger):

    """ Ratpy List Queue class """

    # ####################################################### #
    # ####################################################### #

    name = 'ratpy.queue.list'

    priority = None
    directory = None
    crawler = None

    _list = None
    _total = None

    # ####################################################### #

    def __init__(self, crawler, directory, priority, *args, **kwargs):

        self.priority = str(priority)
        self.directory = os.path.join(directory, '['+self.priority+']')
        self.crawler = crawler
        Logger.__init__(self, self.crawler, directory=self.directory)

        self.logger.debug(action='Initialisation', status='OK', message='[{}]'.format(self.priority))

    # ####################################################### #

    @property
    def infos(self):
        infos = super().infos
        infos['size'] = len(self)
        return infos

    # ####################################################### #

    def open(self):
        self.logger.debug(action='Open', message='[{}]'.format(self.priority))

        self._list = []
        self._total = 0

        self.logger.debug(action='Open', status='OK', message='[{}]'.format(self.priority))

    def close(self):
        self.logger.debug(action='Close', message='[{}]'.format(self.priority))

        for _ in self._list:
            del self._list[0]
            self._total -= 1

        self.logger.debug(action='Close', status='OK', message='[{}]'.format(self.priority))

    # ####################################################### #

    def empty(self):
        return self._total == 0

    def __len__(self):
        return self._total

    # ####################################################### #
    # ####################################################### #

    def push(self, request, timestamp):
        x = (request, timestamp)
        self._list.append(x)
        self._list.sort(key=lambda elem: elem[1])
        self._total += 1
        self.logger.debug(action='Push', status='OK', message='[{}]'.format(self.priority))
        return True

    def pop(self):
        if self._total and self._list[0][1] <= time.time():
            self._total -= 1
            request = self._list.pop(0)[0]
            self.logger.debug(action='Pop', status='OK', message='[{}]'.format(self.priority))
        else:
            request = None
            self.logger.debug(action='Pop', status='NO', message='[{}]'.format(self.priority))
        return request

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
