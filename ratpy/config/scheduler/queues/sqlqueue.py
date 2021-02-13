""" Ratpy Scheduler Queues module """

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

    name = 'queue.sql'

    _TABLE_NAME = 'queue'
    _SQL_CREATE = 'CREATE TABLE IF NOT EXISTS {table_name} (_id INTEGER PRIMARY KEY AUTOINCREMENT, data BLOB, timestamp FLOAT)'
    _SQL_INSERT = 'INSERT INTO {table_name} (data, timestamp) VALUES (?, ?)'
    _SQL_SELECT = 'SELECT _id, data FROM {table_name} WHERE timestamp < ? ORDER BY timestamp ASC LIMIT 1'
    _SQL_DELETE = 'DELETE FROM {table_name} WHERE _id = ?'
    _SQL_COUNT = 'SELECT COUNT(_id) FROM {table_name}'

    work_dir = None
    log_dir = None

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

    def __init__(self, crawler, work_dir, log_dir, multithreading=True, timeout=10.0):

        self.work_dir = work_dir
        self.log_dir = log_dir

        Logger.__init__(self, crawler, log_dir=self.log_dir)

        self.multithreading = multithreading
        self.timeout = timeout

        if self.storage == 'DISK':
            create_directory(self.work_dir)

    # ####################################################### #

    def open(self):

        def open_connection(multithreading, timeout):
            if self.storage == 'MEMORY':
                conn = sqlite3.connect(':memory:', check_same_thread=not multithreading)
            else:
                conn = sqlite3.connect('{}/{}'.format(self.work_dir, 'data.db'), timeout=timeout, check_same_thread=not multithreading)
            conn.execute('PRAGMA journal_mode=WAL;')
            return conn

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

    def close(self):
        self._getter.close()
        self._putter.close()

    # ####################################################### #

    def empty(self):
        return self._total == 0

    def __len__(self):
        return self._total

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
        self._total += 1
        self.put_event.set()
        return True

    def pop(self):
        row = self._select()
        if row and row[0] is not None:
            self._delete(row[0])
            self._total -= 1
            return row[1]
        return None

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
