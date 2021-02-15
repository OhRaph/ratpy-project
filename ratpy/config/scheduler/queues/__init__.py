""" Ratpy Scheduler Queues module """

import os
import pickle
import time

from ratpy.config.scheduler.queues.listqueue import RatpyListQueue
from ratpy.config.scheduler.queues.sqlqueue import RatpySQLQueue
from ratpy.utils import create_instance, Logger, monitored
from ratpy.http.request.serialize import request_to_dict, request_from_dict

# ############################################################### #
# ############################################################### #


def _ratpy_non_serialization_queue(queue_class):

    class RatpyRequestQueue(queue_class):

        spider = None

        def __init__(self, crawler, *args, **kwargs):
            self.spider = crawler.spider
            super(RatpyRequestQueue, self).__init__(crawler, *args, **kwargs)

        @classmethod
        def from_crawler(cls, crawler, *args, **kwargs):
            return cls(crawler, *args, **kwargs)

        @property
        def infos(self):
            infos = super().infos
            infos['class'] = queue_class.__module__ + '.' + queue_class.__name__,
            infos['serialization'] = False
            return infos

    return RatpyRequestQueue

# ############################################################### #


def _ratpy_serialization_queue(queue_class, serialize, deserialize):

    class RatpyRequestQueue(queue_class):

        spider = None

        def __init__(self, crawler, *args, **kwargs):
            self.spider = crawler.spider
            super(RatpyRequestQueue, self).__init__(crawler, *args, **kwargs)

        @classmethod
        def from_crawler(cls, crawler, *args, **kwargs):
            return cls(crawler, *args, **kwargs)

        @property
        def infos(self):
            infos = super().infos
            infos['class'] = queue_class.__module__ + '.' + queue_class.__name__
            infos['serialization'] = True
            return infos

        def push(self, request, timestamp):
            dictionnary = request_to_dict(request, self.spider)
            serialized = serialize(dictionnary)
            return super(RatpyRequestQueue, self).push(serialized, timestamp)

        def pop(self):
            serialized = super(RatpyRequestQueue, self).pop()
            dictionnary = deserialize(serialized) if serialized else None
            return request_from_dict(dictionnary, self.spider)

    return RatpyRequestQueue

# ############################################################### #


def _pickle_serialize(obj):
    try:
        return pickle.dumps(obj, protocol=4)
    except (pickle.PicklingError, AttributeError, TypeError) as _e:
        raise ValueError(str(_e)) from _e

# ############################################################### #
# ############################################################### #


RatpyMemoryQueue = _ratpy_non_serialization_queue(RatpyListQueue)
RatpyDiskQueue = _ratpy_serialization_queue(RatpySQLQueue, _pickle_serialize, pickle.loads)

# ############################################################### #
# ############################################################### #


@monitored
class RatpyPriorityQueue(Logger):

    """ Ratpy Priority Queue class """

    # ####################################################### #
    # ####################################################### #

    name = 'ratpy.queue.priority'

    directory = None
    crawler = None
    spider = None

    queues_type = None
    queues_cls = None
    queues = None
    start_prios = None

    # ####################################################### #

    def __init__(self, crawler, queues_type, queues_cls, directory, start_prios=()):
        self.name = self.name + '.' + queues_type
        self.directory = os.path.join(directory, self.name)
        self.crawler = crawler
        self.spider = crawler.spider
        Logger.__init__(self, self.crawler, directory=self.directory)

        self.queues_type = queues_type
        self.queues_cls = queues_cls
        self.queues = {}
        self.start_prios = start_prios

        self.logger.debug('{:_<18} : OK'.format('Initialisation'))

    @classmethod
    def from_crawler(cls, crawler, type, queues_cls, dir, start_prios=()):
        return cls(crawler, type, queues_cls, dir, start_prios)

    # ####################################################### #

    @property
    def infos(self):
        infos = super().infos
        infos['size'] = len(self)
        infos['queues'] = {priority: queue.infos for priority, queue in self.queues.items()}
        return infos

    # ####################################################### #

    def open(self):
        self.logger.debug('{:_<18}'.format('Open'))

        for priority in self.start_prios:
            self.queues[priority] = self.qfactory(priority)
            self.queues[priority].open()

        self.logger.info('{:_<18} : OK'.format('Open'))

    def close(self):
        self.logger.debug('{:_<18}'.format('Close'))

        active = []

        for _p in sorted(self.queues):
            active.append(_p)
            self.queues[_p].close()

        self.logger.info('{:_<18} : OK'.format('Close'))

        return active

    # ####################################################### #

    def __len__(self):
        return sum(len(x) for x in self.queues.values()) if self.queues else 0

    # ####################################################### #

    def qfactory(self, priority):
        return create_instance(self.queues_cls, None, self.crawler, self.directory, priority)

    def push(self, request):
        priority = -request.priority
        if priority not in self.queues:
            self.queues[priority] = self.qfactory(priority)
            self.queues[priority].open()

        timestamp = request.timestamp or time.time()

        success = self.queues[priority].push(request, timestamp)
        if success:
            self.crawler.stats.inc_value('scheduler/queue/{}/remaining/[all]'.format(self.queues_type), spider=self.spider)
            self.crawler.stats.inc_value('scheduler/queue/{}/remaining/[{: >3}]'.format(self.queues_type, priority), spider=self.spider)
            self.logger.debug('{:_<18} : OK   {} [{}]'.format('Push', request.url, timestamp))
        else:
            self.logger.debug('{:_<18} : NO   {} [{}]'.format('Push', request.url, timestamp))
        return success

    def pop(self):
        request = None

        for priority in sorted(self.queues):
            if len(self.queues[priority]):
                request = self.queues[priority].pop()
                if request is not None:
                    self.crawler.stats.dec_value('scheduler/queue/{}/remaining/[all]'.format(self.queues_type), spider=self.spider)
                    self.crawler.stats.dec_value('scheduler/queue/{}/remaining/[{: >3}]'.format(self.queues_type, priority), spider=self.spider)
                    break

        if request is not None:
            self.logger.debug('{:_<18} : OK   {}'.format('Pop', request.url))
        else:
            self.logger.debug('{:_<18} : NO'.format('Pop'))
        return request

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
