""" Ratpy Logger module """

import logging
import os

from ratpy.utils.path import log_directory, create_file

# ############################################################### #
# ############################################################### #

DEFAULT_DIR = './'


class Logger:

    """ Ratpy Logger class """

    # ####################################################### #
    # ####################################################### #

    name = 'ratpy.logger'
    directory = None

    crawler = None

    log_file = None
    _logger = None

    # ####################################################### #

    def __init__(self, crawler, *args, directory=DEFAULT_DIR, **kwargs):

        self.directory = directory
        self.crawler = crawler

        self.log_file = os.path.join(log_directory(self.crawler.settings), self.directory, self.name + '.log')
        if self.crawler.settings.get('LOG_IN_FILES'):
            create_file(self.log_file, 'w+', '')

    # ####################################################### #
    # ####################################################### #

    @property
    def logger(self):

        if self._logger is None:
            self._logger = create_logger(self)

        return self._logger

    # ####################################################### #

    @property
    def infos(self):
        return {
            # 'id': id(self)
            'name': self.name,
            'class': self.__module__ + '.' + self.__class__.__name__,
            'log_file': self.log_file
            }

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #


def create_logger(obj):

    class _Logger:

        def __init__(self):

            name_pattern = '{:_<' + str(obj.crawler.settings.getint('LOG_NAME_SIZE')) + '}'
            self._logger = logging.getLogger(name_pattern.format(obj.name))

            formatter = logging.Formatter(
                fmt=obj.crawler.settings.get('LOG_FORMAT'),
                datefmt=obj.crawler.settings.get('LOG_DATEFORMAT')
            )

            if not obj.crawler.settings.getbool('LOG_ENABLED'):
                self._logger.handlers = []
                handler = logging.NullHandler()
                self._logger.addHandler(handler)

            if obj.crawler.settings.get('LOG_IN_FILES'):
                handler = logging.FileHandler(obj.log_file, encoding=obj.crawler.settings.get('LOG_ENCODING'))
                handler.setFormatter(formatter)
                handler.setLevel(obj.crawler.settings.get('LOG_LEVEL_IN_FILES'))
                self._logger.addHandler(handler)

            if obj.crawler.settings.get('LOG_IN_ONE_FILE'):
                handler_all = logging.FileHandler(os.path.join(log_directory(obj.crawler.settings), 'ratpy.log'), encoding=obj.crawler.settings.get('LOG_ENCODING'))
                handler_all.setFormatter(formatter)
                handler_all.setLevel(obj.crawler.settings.get('LOG_LEVEL_IN_ONE_FILE'))
                self._logger.addHandler(handler_all)

        def debug(self, *args, action=None, status=None, message='', **kwargs):
            self._log(logging.DEBUG, *args, action=action, status=status, message=message, **kwargs)

        def info(self, *args, action=None, status=None, message='', **kwargs):
            self._log(logging.INFO, *args, action=action, status=status, message=message, **kwargs)

        def warning(self, *args, action=None, status=None, message='', **kwargs):
            self._log(logging.WARNING, *args, action=action, status=status, message=message, **kwargs)

        def error(self, *args, action=None, status=None, message='', **kwargs):
            self._log(logging.ERROR, *args, action=action, status=status, message=message, **kwargs)

        def critical(self, *args, action=None, status=None, message='', **kwargs):
            self._log(logging.CRITICAL, *args, action=action, status=status, message=message, **kwargs)

        def _log(self, level, *args, action=None, status=None, message='', **kwargs):

            if action is not None:
                if status is not None:
                    self._logger.log(level, '{:_<18} : {: <5} {}'.format(action, status, message))
                else:
                    self._logger.log(level, '{:_<18}         {}'.format(action, message))
            else:
                self._logger.log(level, *args, **kwargs)

    return _Logger()

# ############################################################### #
# ############################################################### #
