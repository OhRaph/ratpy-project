""" Ratpy Monitor module """

import os
import time

import inspect

from ratpy.utils.path import monitor_directory, create_file

# ############################################################### #
# ############################################################### #


def _save_crawler(obj, crawler):
    obj._monitor_crawler = crawler


def _save_original_functions(obj):
    obj._monitor_original_functions = {}
    for x in filter(lambda x: not x[0].startswith('_'), inspect.getmembers(obj.__class__, predicate=inspect.isfunction)):
        obj._monitor_original_functions[x[0]] = x[1]

# ############################################################### #


def _add_decorator_x(obj, func):
    def _execute(*args, **kwargs):
        return time.time(), func(obj, *args, **kwargs), time.time()
    return _execute

# ############################################################### #


def _init_store(obj):
    obj._monitor_store = []

    for name, func in obj._monitor_original_functions.items():
        setattr(obj, name, _add_decorator_xs(obj, name, func))


def _del_store(obj):
    obj._monitor_store = None


def _store(obj, name, start, res, end):
    obj._monitor_store.append((name, start, res, end))


def _add_decorator_xs(obj, name, func):
    def _execute(*args, **kwargs):
        start, res, end = _add_decorator_x(obj, func)(*args, **kwargs)
        _store(obj, name, start, res, end)
        return res
    return _execute

# ############################################################### #


def _init_write(obj):
    monitor_dir = os.path.join(monitor_directory(obj._monitor_crawler.settings), getattr(obj, 'directory', ''))
    monitor_file = os.path.join(monitor_dir, getattr(obj, 'name', obj.__class__.__name__) + '.monitor.csv')
    create_file(monitor_file, 'w+', 'id,function,start,end,duration,output\n')
    obj._monitor_write = open(monitor_file, 'a+')

    for name, func in obj._monitor_original_functions.items():
        setattr(obj, name, _add_decorator_xw(obj, name, func))


def _del_write(obj):
    obj._monitor_write.close()


def _write(obj, name, start, res, end):
    obj._monitor_write.write('{},{},{},{},{},{}\n'.format(id(obj), name, start, end, end - start, type(res)))


def _add_decorator_xw(obj, name, func):
    def _execute(*args, **kwargs):
        start, res, end = _add_decorator_x(obj, func)(*args, **kwargs)
        _write(obj, name, start, res, end)
        return res
    return _execute

# ############################################################### #


def monitored(monitored_class):

    _monitored_init = monitored_class.__init__ if hasattr(monitored_class, '__init__') else None
    _monitored_del = monitored_class.__del__ if hasattr(monitored_class, '__del__') else None

    def __init__(self, crawler, *args, **kwargs):

        _save_crawler(self, crawler)

        if self._monitor_crawler.settings.get('MONITOR_ENABLED'):
            _save_original_functions(self)
            _init_store(self)

            if _monitored_init is not None:
                x_init = _add_decorator_x(self, _monitored_init)(crawler, *args, **kwargs)
                _init_write(self)
                _write(self, '__init__', *x_init)
            else:
                _init_write(self)

            [_write(self, *s_func) for s_func in self._monitor_store]
            _del_store(self)
        else:
            if _monitored_init is not None:
                _monitored_init(self, crawler, *args, **kwargs)

    def __del__(self, *args, **kwargs):

        if self._monitor_crawler.settings.get('MONITOR_ENABLED'):
            if _monitored_del is not None:
                x_del = _add_decorator_x(self, _monitored_del)(*args, **kwargs)
                _write(self, '__del__', *x_del)
            _del_write(self)
        else:
            if _monitored_del is not None:
                _monitored_del(self, *args, **kwargs)

    monitored_class.__init__ = __init__
    monitored_class.__del__ = __del__

    return monitored_class

# ############################################################### #
# ############################################################### #
