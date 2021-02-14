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

    crawler = None

    log_file = None
    _logger = None

    # ####################################################### #

    def __init__(self, crawler, *args, directory=DEFAULT_DIR, **kwargs):

        self.crawler = crawler

        self.log_file = os.path.join(log_directory(self.crawler.settings), directory, self.name+'.log')
        create_file(self.log_file, 'w+', '')

    # ####################################################### #
    # ####################################################### #

    @property
    def logger(self):

        if self._logger is None:

            self._logger = logging.getLogger('{:_<55}'.format(self.name))

            formatter = logging.Formatter(
                fmt=self.crawler.settings.get('LOG_FORMAT'),
                datefmt=self.crawler.settings.get('LOG_DATEFORMAT')
            )

            if not self.crawler.settings.getbool('LOG_ENABLED'):
                self._logger.handlers = []
                handler = logging.NullHandler()
                self._logger.addHandler(handler)

            if self.crawler.settings.get('LOG_IN_FILES'):
                handler = logging.FileHandler(self.log_file, encoding=self.crawler.settings.get('LOG_ENCODING'))
                handler.setFormatter(formatter)
                handler.setLevel(self.crawler.settings.get('LOG_LEVEL_IN_FILES'))
                self._logger.addHandler(handler)

            if self.crawler.settings.get('LOG_IN_ONE_FILE'):
                handler_all = logging.FileHandler(os.path.join(log_directory(self.crawler.settings), 'ratpy.log'), encoding=self.crawler.settings.get('LOG_ENCODING'))
                handler_all.setFormatter(formatter)
                handler_all.setLevel(self.crawler.settings.get('LOG_LEVEL_IN_ONE_FILE'))
                self._logger.addHandler(handler_all)

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
