""" Ratpy Monitor module """

import os
import time

import inspect

from ratpy.utils.path import monitor_directory, create_directory

# ############################################################### #
# ############################################################### #

DEFAULT_DIR = './'


def filter_function(name):

    if name.startswith('_'):
        return False
    if name in ['open', 'close', 'add_decorator']:
        return False
    return True


class Monitor:

    """ Ratpy Monitor class """

    # ####################################################### #
    # ####################################################### #

    name = 'ratpy.monitor'
    directory = None

    crawler = None

    monitor_dir = None

    monitored_functions = None

    # ####################################################### #

    def __init__(self, crawler, *args, directory=DEFAULT_DIR, **kwargs):

        self.directory = directory
        self.crawler = crawler

        self.monitor_dir = os.path.join(monitor_directory(self.crawler.settings), self.directory, 'monitors')
        if self.crawler.settings.get('MONITOR_ENABLED'):
            create_directory(self.monitor_dir)

        self.monitored_functions = {}

    # ####################################################### #
    # ####################################################### #

    def open(self, *args, **kwargs):

        if self.crawler.settings.get('MONITOR_ENABLED'):
            for x in filter(lambda x: filter_function(x[0]), inspect.getmembers(self.__class__, predicate=inspect.isfunction)):
                self.monitored_functions[x[0]] = open(os.path.join(self.monitor_dir, x[0]+'.csv'), 'w+')
                setattr(self, x[0], self.add_decorator(x[1]))

    def close(self, *args, **kwargs):

        if self.crawler.settings.get('MONITOR_ENABLED'):
            for function in self.monitored_functions:
                self.monitored_functions[function].close()

    # ####################################################### #
    # ####################################################### #

    def add_decorator(self, func):

        def _execute(*args, **kwargs):
            start = time.time() * 1000
            res = func(self, *args, **kwargs)
            end = time.time() * 1000
            # print('{: <45} | {: <20} | {}'.format(self.name, func.__name__, self.monitored_functions[func.__name__].name))
            self.monitored_functions[func.__name__].write('{},{},{}\n'.format(start, end, end-start))
            return res

        return _execute

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
