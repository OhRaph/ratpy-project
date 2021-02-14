""" Ratpy Scheduler Queues module """

import os
import sqlite3
import threading
import time

from ratpy.utils import Logger, Monitor
from ratpy.utils.path import create_directory, work_directory

# ############################################################### #
# ############################################################### #

sqlite3.enable_callback_tracebacks(True)

# ############################################################### #


class RatpySQLQueue(Logger, Monitor):

    """ Ratpy SQL Queue class """

    # ####################################################### #
    # ####################################################### #

    name = 'ratpy.queue.sql'

    priority = None
    directory = None
    crawler = None

    work_file = None

    storage = 'DISK'
    timeout = None
    multithreading = None

    _conn = None
    _getter = None
    _putter = None

    _total = None

    transaction_lock = None
    put_event = None

    _TABLE_NAME = 'queue'
    _SQL_CREATE = 'CREATE TABLE IF NOT EXISTS {table_name} (_id INTEGER PRIMARY KEY AUTOINCREMENT, data BLOB, timestamp FLOAT)'
    _SQL_INSERT = 'INSERT INTO {table_name} (data, timestamp) VALUES (?, ?)'
    _SQL_SELECT = 'SELECT _id, data FROM {table_name} WHERE timestamp < ? ORDER BY timestamp ASC LIMIT 1'
    _SQL_DELETE = 'DELETE FROM {table_name} WHERE _id = ?'
    _SQL_COUNT = 'SELECT COUNT(_id) FROM {table_name}'
    _SQL_SELECT_OLDER_TIMESTAMP = 'SELECT timestamp FROM {table_name} ORDER BY timestamp ASC LIMIT 1'

    # ####################################################### #

    def __init__(self, crawler, directory, priority, *args, multithreading=True, timeout=10.0, **kwargs):

        self.priority = str(priority)
        self.directory = os.path.join(directory, '['+self.priority+']')
        self.crawler = crawler
        Monitor.__init__(self, crawler, directory=self.directory)
        Logger.__init__(self, crawler, directory=self.directory)

        self.multithreading = multithreading
        self.timeout = timeout

        self.logger.debug('{:_<18} : OK   [{}]'.format('Initialisation', self.priority))

    # ####################################################### #

    @property
    def infos(self):
        infos = super().infos
        infos['work_file'] = self.work_file
        infos['size'] = len(self)
        return infos

    # ####################################################### #

    def open(self):

        def open_connection(multithreading, timeout):
            if self.storage == 'MEMORY':
                conn = sqlite3.connect(':memory:', check_same_thread=not multithreading)
            else:
                work_dir = os.path.join(work_directory(self.crawler.settings), self.directory)
                create_directory(work_dir)
                self.work_file = os.path.join(work_dir, self.name+'.db')
                conn = sqlite3.connect(self.work_file, timeout=timeout, check_same_thread=not multithreading)
            conn.execute('PRAGMA journal_mode=WAL;')
            return conn

        self.logger.debug('{:_<18}        [{}]'.format('Open', self.priority))
        Monitor.open(self)

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
        Monitor.close(self)

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

    def _insert(self, request, timestamp):
        args = (request, timestamp)
        with self.transaction_lock:
            with self._putter:
                return self._putter.execute(self._sql_insert(), args)

    def _select(self):
        args = (time.time(),)
        return self._getter.execute(self._sql_select(), args).fetchone()

    def _delete(self, key):
        args = (key,)
        with self.transaction_lock:
            with self._putter:
                return self._putter.execute(self._sql_delete(), args)

    def _count(self):
        args = ()
        row = self._getter.execute(self._sql_count(), args).fetchone()
        return row[0] if row else 0

    def _select_older_timestamp(self):
        args = ()
        row = self._getter.execute(self._sql_select_older_timestamp(), args).fetchone()
        return row[0] if row else None

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

    def _sql_select_older_timestamp(self):
        return self._SQL_SELECT_OLDER_TIMESTAMP.format(table_name=self._table_name)

    # ####################################################### #

    def push(self, request, timestamp):
        self._insert(request, timestamp)
        self.put_event.set()
        self._total += 1
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
