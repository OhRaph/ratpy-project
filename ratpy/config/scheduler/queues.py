""" Ratpy Scheduler Queues module """

import os
import marshal
import pickle

from queuelib import queue

from ratpy.utils import create_instance
from ratpy.http.request.serialize import request_to_dict, request_from_dict

# ############################################################### #
# ############################################################### #


def _with_mkdir(queue_class):

    class DirectoriesCreated(queue_class):

        def __init__(self, path, *args, **kwargs):
            dirname = os.path.dirname(path)
            if not os.path.exists(dirname):
                os.makedirs(dirname, exist_ok=True)
            super(DirectoriesCreated, self).__init__(path, *args, **kwargs)

    return DirectoriesCreated

# ############################################################### #


def _serializable_queue(queue_class, serialize, deserialize):

    class SerializableQueue(queue_class):

        def push(self, obj):
            _s = serialize(obj)
            super(SerializableQueue, self).push(_s)

        def pop(self):
            _s = super(SerializableQueue, self).pop()
            return deserialize(_s) if _s else None

    return SerializableQueue

# ############################################################### #


def _ratpy_serialization_queue(queue_class):

    class RatpyRequestQueue(queue_class):

        def __init__(self, crawler, key, *args, **kwargs):
            self.spider = crawler.spider
            super(RatpyRequestQueue, self).__init__(key)

        @classmethod
        def from_crawler(cls, crawler, key):
            return cls(crawler, key)

        def push(self, request):
            request = request_to_dict(request, self.spider)
            return super(RatpyRequestQueue, self).push(request)

        def pop(self):
            request = super(RatpyRequestQueue, self).pop()
            return request_from_dict(request, self.spider)

    return RatpyRequestQueue

# ############################################################### #


def _ratpy_non_serialization_queue(queue_class):

    class RatpyRequestQueue(queue_class):
        @classmethod
        def from_crawler(cls, crawler, *args, **kwargs):
            return cls()

    return RatpyRequestQueue

# ############################################################### #


def _pickle_serialize(obj):
    try:
        return pickle.dumps(obj, protocol=4)
    except (pickle.PicklingError, AttributeError, TypeError) as _e:
        raise ValueError(str(_e)) from _e

# ############################################################### #
# ############################################################### #


PickleFifoDiskQueueNonRequest = _serializable_queue(_with_mkdir(queue.FifoDiskQueue), _pickle_serialize, pickle.loads)
PickleLifoDiskQueueNonRequest = _serializable_queue(_with_mkdir(queue.LifoDiskQueue), _pickle_serialize, pickle.loads)
MarshalFifoDiskQueueNonRequest = _serializable_queue(_with_mkdir(queue.FifoDiskQueue), marshal.dumps, marshal.loads)
MarshalLifoDiskQueueNonRequest = _serializable_queue(_with_mkdir(queue.LifoDiskQueue), marshal.dumps, marshal.loads)

PickleFifoDiskQueue = _ratpy_serialization_queue(PickleFifoDiskQueueNonRequest)
PickleLifoDiskQueue = _ratpy_serialization_queue(PickleLifoDiskQueueNonRequest)
MarshalFifoDiskQueue = _ratpy_serialization_queue(MarshalFifoDiskQueueNonRequest)
MarshalLifoDiskQueue = _ratpy_serialization_queue(MarshalLifoDiskQueueNonRequest)

FifoMemoryQueue = _ratpy_non_serialization_queue(queue.FifoMemoryQueue)
LifoMemoryQueue = _ratpy_non_serialization_queue(queue.LifoMemoryQueue)

# ############################################################### #
# ############################################################### #


class RatpyPriorityQueue:

    """ Ratpy Priority Queue class """

    # ####################################################### #
    # ####################################################### #

    def __init__(self, crawler, downstream_queue_cls, key, startprios=()):
        self.crawler = crawler
        self.downstream_queue_cls = downstream_queue_cls
        self.key = key
        self.queues = {}
        self.curprio = None
        self.init_prios(startprios)

    @classmethod
    def from_crawler(cls, crawler, downstream_queue_cls, key, startprios=()):
        return cls(crawler, downstream_queue_cls, key, startprios)

    def __len__(self):
        return sum(len(x) for x in self.queues.values()) if self.queues else 0

    # ####################################################### #

    def init_prios(self, startprios):
        if not startprios:
            return

        for priority in startprios:
            self.queues[priority] = self.qfactory(priority)

        self.curprio = min(startprios)

    def qfactory(self, key):
        return create_instance(self.downstream_queue_cls, None, self.crawler, self.key + '/' + str(key))

    # ####################################################### #

    def close(self):
        active = []
        for _p, _q in self.queues.items():
            active.append(_p)
            _q.close()
        return active

    # ####################################################### #

    @staticmethod
    def priority(request):
        return -request.priority

    def push(self, request):
        priority = RatpyPriorityQueue.priority(request)
        if priority not in self.queues:
            self.queues[priority] = self.qfactory(priority)
        _q = self.queues[priority]
        _q.push(request)
        if self.curprio is None or priority < self.curprio:
            self.curprio = priority

    def pop(self):
        if self.curprio is None:
            return None
        _q = self.queues[self.curprio]
        _m = _q.pop()
        if not _q:
            del self.queues[self.curprio]
            _q.close()
            prios = [_p for _p, _q in self.queues.items() if _q]
            self.curprio = min(prios) if prios else None
        return _m

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
