""" Ratpy Scheduler Queues module """

import time

import pickle

from ratpy.config.scheduler.queues.listqueue import RatpyListQueue
from ratpy.config.scheduler.queues.sqlqueue import RatpySQLQueue
from ratpy.utils import create_instance, Logger
from ratpy.http.request.serialize import request_to_dict, request_from_dict

# ############################################################### #
# ############################################################### #


def _ratpy_non_serialization_queue(queue_class):

    class RatpyRequestQueue(queue_class):

        spider = None

        def __init__(self, crawler, work_dir, log_dir, *args, **kwargs):
            self.spider = crawler.spider
            super(RatpyRequestQueue, self).__init__(crawler, work_dir, log_dir)

        @classmethod
        def from_crawler(cls, crawler, work_dir, log_dir, *args, **kwargs):
            return cls(crawler, work_dir, log_dir)

    return RatpyRequestQueue

# ############################################################### #


def _ratpy_serialization_queue(queue_class, serialize, deserialize):

    class RatpyRequestQueue(queue_class):

        spider = None

        def __init__(self, crawler, work_dir, log_dir, *args, **kwargs):
            self.spider = crawler.spider
            super(RatpyRequestQueue, self).__init__(crawler, work_dir, log_dir)

        @classmethod
        def from_crawler(cls, crawler, work_dir, log_dir, *args, **kwargs):
            return cls(crawler, work_dir, log_dir)

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


class RatpyPriorityQueue(Logger):

    """ Ratpy Priority Queue class """

    # ####################################################### #
    # ####################################################### #

    name = 'queue.priority'

    crawler = None

    work_dir = None
    log_dir = None

    queue_cls = None
    queues = None
    start_prios = None

    # ####################################################### #

    def __init__(self, crawler, queue_cls, work_dir, log_dir, start_prios=()):
        self.crawler = crawler
        self.queue_cls = queue_cls
        self.queues = {}
        self.start_prios = start_prios

        self.work_dir = work_dir
        self.log_dir = log_dir

        Logger.__init__(self, self.crawler, log_dir=self.log_dir)

    @classmethod
    def from_crawler(cls, crawler, queue_cls, work_dir, log_dir, start_prios=()):
        return cls(crawler, queue_cls, work_dir, log_dir, start_prios)

    # ####################################################### #

    def open(self):
        if not self.start_prios:
            return

        for priority in self.start_prios:
            self.queues[priority] = self.qfactory(priority)
            self.queues[priority].open()

    def close(self):
        active = []
        for _p in sorted(self.queues):
            active.append(_p)
            self.queues[_p].close()
        return active

    # ####################################################### #

    def __len__(self):
        return sum(len(x) for x in self.queues.values()) if self.queues else 0

    # ####################################################### #

    def qfactory(self, priority):
        return create_instance(self.queue_cls, None, self.crawler, self.work_dir + '/' + str(priority), self.log_dir + '/' + str(priority))

    @staticmethod
    def priority(request):
        return -request.priority

    def push(self, request):
        priority = RatpyPriorityQueue.priority(request)
        if priority not in self.queues:
            self.queues[priority] = self.qfactory(priority)
            self.queues[priority].open()
        timestamp = request.timestamp or time.time()
        return self.queues[priority].push(request, timestamp)

    def pop(self):
        for priority in sorted(self.queues):
            request = self.queues[priority].pop()
            # if len(self.queues[_p]) == 0:
            #     self.queues[_p].close()
            #     del self.queues[_p]
            if request is not None:
                return request
        return None

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
