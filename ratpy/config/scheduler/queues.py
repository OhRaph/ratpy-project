""" Ratpy Scheduler Queues module """

import os
import sqlite3
import threading
import time

import marshal
import pickle

from ratpy.utils import create_instance
from ratpy.http.request.serialize import request_to_dict, request_from_dict

# ############################################################### #
# ############################################################### #

sqlite3.enable_callback_tracebacks(True)

# ############################################################### #


def with_conditional_transaction(func):
    def _execute(obj, *args, **kwargs):
        with obj.transaction_lock:
            with obj._putter as tran:
                stat, param = func(obj, *args, **kwargs)
                tran.execute(stat, param)
    return _execute

# ############################################################### #


class RatpySQLQueue(object):

    # ####################################################### #
    # ####################################################### #

    _TABLE_NAME = 'queue'
    _SQL_CREATE = 'CREATE TABLE IF NOT EXISTS {table_name} (_id INTEGER PRIMARY KEY AUTOINCREMENT, data BLOB, timestamp FLOAT)'
    _SQL_INSERT = 'INSERT INTO {table_name} (data, timestamp) VALUES (?, ?)'
    _SQL_SELECT = 'SELECT _id, data FROM {table_name} WHERE timestamp < ? ORDER BY timestamp ASC LIMIT 1'
    _SQL_DELETE = 'DELETE FROM {table_name} WHERE _id = ?'
    _SQL_COUNT = 'SELECT COUNT(_id) FROM {table_name}'

    _WORK = None

    path = None
    name = None
    timeout = None
    multithreading = None

    _conn = None
    _getter = None
    _putter = None

    # ####################################################### #

    def __init__(self, path, name='default', multithreading=True, timeout=10.0):

        self.path = path
        self.name = name
        self.timeout = timeout
        self.multithreading = multithreading

        if self._WORK == 'DISK':
            if not os.path.exists(self.path):
                os.makedirs(self.path)

        self._conn = self._new_db_connection(self.multithreading, self.timeout)
        self._getter = self._conn
        self._putter = self._conn

        self._conn.execute(self._sql_create())
        self._conn.commit()

        if self._WORK == 'DISK':
            if self.multithreading:
                self._putter = self._new_db_connection(self.multithreading, self.timeout)

        self._conn.text_factory = str
        self._putter.text_factory = str

        self.transaction_lock = threading.Lock()
        self.put_event = threading.Event()
        self.total = self._count()

    def _new_db_connection(self, multithreading, timeout):
        if self._WORK == 'MEMORY':
            conn = sqlite3.connect(':memory:', check_same_thread=not multithreading)
        else:
            conn = sqlite3.connect('{}/{}'.format(self.path, 'data.db'), timeout=timeout, check_same_thread=not multithreading)
        conn.execute('PRAGMA journal_mode=WAL;')
        return conn

    def empty(self):
        return self.total == 0

    def close(self):
        self._getter.close()
        self._putter.close()

    def __len__(self):
        return self.total

    def __del__(self):
        self.close()

    # ####################################################### #
    # ####################################################### #

    @with_conditional_transaction
    def _insert(self, item, timestamp):
        args = (item, timestamp)
        return self._sql_insert(), args

    def _select(self):
        args = (time.time(),)
        return self._getter.execute(self._sql_select(), args).fetchone()

    @with_conditional_transaction
    def _delete(self, key):
        args = (key,)
        return self._sql_delete(), args

    def _count(self):
        args = ()
        row = self._getter.execute(self._sql_count(), args).fetchone()
        return row[0] if row else 0

    # ####################################################### #

    @property
    def _table_name(self):
        return '`{}_{}`'.format(self._TABLE_NAME, self.name)

    def _sql_create(self):
        return self._SQL_CREATE.format(table_name=self._table_name)

    def _sql_insert(self):
        return self._SQL_INSERT.format(table_name=self._table_name)

    def _sql_select(self):
        return self._SQL_SELECT.format(table_name=self._table_name)

    def _sql_delete(self):
        return self._SQL_DELETE.format(table_name=self._table_name)

    def _sql_count(self):
        return self._SQL_COUNT.format(table_name=self._table_name)

    # ####################################################### #

    def push(self, item, timestamp):
        self._insert(item, timestamp)
        self.total += 1
        self.put_event.set()
        return True

    def pop(self):
        row = self._select()
        if row and row[0] is not None:
            self._delete(row[0])
            self.total -= 1
            return row[1]
        return None

    # ####################################################### #
    # ####################################################### #

# ############################################################### #


class RatpyMemorySQLQueue(RatpySQLQueue):
    _WORK = 'MEMORY'


class RatpyDiskSQLQueue(RatpySQLQueue):
    _WORK = 'DISK'

# ############################################################### #
# ############################################################### #


def _serializable_queue(queue_class, serialize, deserialize):

    class SerializableQueue(queue_class):

        def push(self, request, timestamp):
            _s = serialize(request)
            super(SerializableQueue, self).push(_s, timestamp)

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

        def push(self, request, timestamp):
            request = request_to_dict(request, self.spider)
            return super(RatpyRequestQueue, self).push(request, timestamp)

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


PickleDiskQueue = _ratpy_serialization_queue(_serializable_queue(RatpyDiskSQLQueue, _pickle_serialize, pickle.loads))
MarshalDiskQueue = _ratpy_serialization_queue(_serializable_queue(RatpyDiskSQLQueue, marshal.dumps, marshal.loads))

PickleMemoryQueue = _ratpy_serialization_queue(_serializable_queue(RatpyMemorySQLQueue, _pickle_serialize, pickle.loads))
MarshalMemoryQueue = _ratpy_serialization_queue(_serializable_queue(RatpyMemorySQLQueue, marshal.dumps, marshal.loads))

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

    def qfactory(self, key):
        return create_instance(self.downstream_queue_cls, None, self.crawler, self.key + '/' + str(key))

    # ####################################################### #

    def close(self):
        active = []
        for _p in sorted(self.queues):
            active.append(_p)
            self.queues[_p].close()
        return active

    # ####################################################### #

    @staticmethod
    def priority(request):
        return -request.priority

    def push(self, request):
        priority = RatpyPriorityQueue.priority(request)
        if priority not in self.queues:
            self.queues[priority] = self.qfactory(priority)
        timestamp = request.timestamp or time.time()
        return self.queues[priority].push(request, timestamp)

    def pop(self):
        for _p in sorted(self.queues):
            _m = self.queues[_p].pop()
            # if len(self.queues[_p]) == 0:
            #     self.queues[_p].close()
            #     del self.queues[_p]
            if _m is not None:
                return _m
        return None

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
