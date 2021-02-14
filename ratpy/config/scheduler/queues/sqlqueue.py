""" Ratpy Scheduler Queues module """

import os
import sqlite3
import threading
import time

from ratpy.utils import Logger
from ratpy.utils.path import create_directory

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


class RatpySQLQueue(Logger):

    """ Ratpy SQL Queue class """

    # ####################################################### #
    # ####################################################### #

    name = 'ratpy.queue.sql'
    priority = None

    _TABLE_NAME = 'queue'
    _SQL_CREATE = 'CREATE TABLE IF NOT EXISTS {table_name} (_id INTEGER PRIMARY KEY AUTOINCREMENT, data BLOB, timestamp FLOAT)'
    _SQL_INSERT = 'INSERT INTO {table_name} (data, timestamp) VALUES (?, ?)'
    _SQL_SELECT = 'SELECT _id, data FROM {table_name} WHERE timestamp < ? ORDER BY timestamp ASC LIMIT 1'
    _SQL_DELETE = 'DELETE FROM {table_name} WHERE _id = ?'
    _SQL_COUNT = 'SELECT COUNT(_id) FROM {table_name}'

    work_path = None

    storage = 'DISK'
    timeout = None
    multithreading = None

    _conn = None
    _getter = None
    _putter = None

    _total = None

    transaction_lock = None
    put_event = None

    # ####################################################### #

    def __init__(self, crawler, priority, work_dir, log_dir, *args, multithreading=True, timeout=10.0, **kwargs):

        self.priority = str(priority)

        self.multithreading = multithreading
        self.timeout = timeout

        self.work_path = os.path.join(work_dir, '['+self.priority+']', self.name+'.db')
        if self.storage == 'DISK':
            create_directory(os.path.join(work_dir, '['+self.priority+']'))

        Logger.__init__(self, crawler, log_dir=os.path.join(log_dir, '['+self.priority+']'))

        self.logger.debug('{:_<18} : OK   [{}]'.format('Initialisation', self.priority))

    # ####################################################### #

    @property
    def infos(self):
        infos = super().infos
        infos['work_path'] = self.work_path
        infos['size'] = len(self)
        return infos

    # ####################################################### #

    def open(self):

        def open_connection(multithreading, timeout):
            if self.storage == 'MEMORY':
                conn = sqlite3.connect(':memory:', check_same_thread=not multithreading)
            else:
                conn = sqlite3.connect(self.work_path, timeout=timeout, check_same_thread=not multithreading)
            conn.execute('PRAGMA journal_mode=WAL;')
            return conn

        self.logger.debug('{:_<18}        [{}]'.format('Open', self.priority))

        self._conn = open_connection(self.multithreading, self.timeout)
        self._conn.execute(self._sql_create())
        self._conn.commit()

        self._getter = self._conn
        self._putter = self._conn
        if self.storage == 'DISK':
            if self.multithreading:
                self._putter = open_connection(self.multithreading, self.timeout)

        self._conn.text_factory = str
        self._putter.text_factory = str

        self.transaction_lock = threading.Lock()
        self.put_event = threading.Event()

        self._total = self._count()

        self.logger.debug('{:_<18} : OK   [{}]'.format('Open', self.priority))

    def close(self):
        self.logger.debug('{:_<18}        [{}]'.format('Close', self.priority))

        self._getter.close()
        self._putter.close()

        self.logger.debug('{:_<18} : OK   [{}]'.format('Close', self.priority))

    # ####################################################### #

    def empty(self):
        return self._total == 0

    def __len__(self):
        return self._total

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

    def push(self, request, timestamp):
        self._insert(request, timestamp)
        self._total += 1
        self.put_event.set()
        self.logger.debug('{:_<18} : OK   [{}]'.format('Push', self.priority))
        return True

    def pop(self):
        row = self._select()
        if row and row[0] is not None:
            self._delete(row[0])
            self._total -= 1
            request = row[1]
            self.logger.debug('{:_<18} : OK   [{}]'.format('Pop', self.priority))
        else:
            request = None
            self.logger.debug('{:_<18} : NO   [{}]'.format('Pop', self.priority))
        return request

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
