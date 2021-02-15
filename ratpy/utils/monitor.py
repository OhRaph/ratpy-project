""" Ratpy Monitor module """

import os
import time

import inspect

from ratpy.utils.path import monitor_directory, create_file

# ############################################################### #
# ############################################################### #


def add_decorator(obj, name, func):

    def _execute(*args, **kwargs):
        start = time.time()
        res = func(obj, *args, **kwargs)
        end = time.time()
        obj._monitor_file.write('{},{},{},{},{}\n'.format(name, start, end, end - start, type(res)))
        return res

    return _execute

# ############################################################### #


def monitored(monitored_class):

    _monitored_init = monitored_class.__init__ if hasattr(monitored_class, '__init__') else None
    _monitored_del = monitored_class.__del__ if hasattr(monitored_class, '__del__') else None

    def __init__(self, crawler, *args, **kwargs):

        if _monitored_init is not None:
            _monitored_init(self, crawler, *args, **kwargs)

        if self.crawler.settings.get('MONITOR_ENABLED'):

            monitor_file = os.path.join(monitor_directory(self.crawler.settings), self.directory, self.name + '.monitor.csv')
            create_file(monitor_file, 'w+', 'function,start,end,duration,output\n')
            self._monitor_file = open(monitor_file, 'a+')

            self.monitored_functions = {}
            for x in filter(lambda x: not x[0].startswith('_'), inspect.getmembers(self.__class__, predicate=inspect.isfunction)):
                setattr(self, x[0], add_decorator(self, x[0], x[1]))
                self.monitored_functions[x[0]] = (x[1], getattr(self, x[0]))

    def __del__(self, *args, **kwargs):

        if _monitored_del is not None:
            _monitored_del(self, *args, **kwargs)

        if self.crawler.settings.get('MONITOR_ENABLED'):
            self._monitor_file.close()

    monitored_class.__init__ = __init__
    monitored_class.__del__ = __del__

    return monitored_class

# ############################################################### #
# ############################################################### #
