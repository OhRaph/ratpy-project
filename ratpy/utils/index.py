""" Ratpy Index module """

import json
import os
import pandas

from ratpy.utils import Logger, sizeof
from ratpy.utils.path import create_file, work_directory

# ############################################################### #
# ############################################################### #

DEFAULT_DIR = '../'


class Index(Logger):

    """ Ratpy Index class """

    # ####################################################### #
    # ####################################################### #

    name = 'index'

    directory = None
    crawler = None

    work_file = None

    _columns = None
    _index = None

    # ####################################################### #

    def __init__(self, crawler, *args, name=None, directory=DEFAULT_DIR, columns=None, **kwargs):

        if name:
            self.name = name
        self.directory = directory
        self.crawler = crawler

        self._columns = columns
        self._index = pandas.DataFrame([], columns=self._columns)

        Logger.__init__(self, self.crawler, directory=self.directory)

        self.work_file = os.path.join(work_directory(self.crawler.settings), self.directory, self.name+'.csv')
        create_file(self.work_file, 'w+', self._index.to_csv(index=False))

        # self.logger.info(action='Initialisation', status='OK')

    def __str__(self):
        return self.infos.__str__()

    # ####################################################### #

    @property
    def infos(self):
        infos = super().infos
        infos['work_file'] = self.work_file
        infos['counts'] = self.counts
        return infos

    # ####################################################### #

    def open(self):
        # self.logger.debug(action='Open')
        with open(self.work_file, 'r') as file:
            self._index = pandas.read_csv(file)
            file.close()
        self.logger.debug(action='Open', status='OK', message='{}'.format(self.work_file))

    def close(self):
        # self.logger.debug(action='Close')
        if self.crawler.settings.get('WORK_ON_DISK', False):
            with open(self.work_file, 'w+') as file:
                file.write(self._index.to_csv(index=False))
                file.close()
        self.logger.debug(action='Close', status='OK', message='{}'.format(self.work_file))

    # ####################################################### #
    # ####################################################### #

    def __len__(self):
        return len(self._index)

    @property
    def length(self):
        return self.__len__()

    @property
    def counts(self):
        return {column: self._index[column].nunique() for column in self._columns}

    @property
    def size(self):
        return int(sizeof(self._index)/1000)

    # ####################################################### #

    def add(self, **kwargs):

        self._index = self._index.append(kwargs, ignore_index=True)

        self.logger.debug(action='Index (+)', status='OK', message='{}'.format(json.dumps(kwargs, indent=None, sort_keys=False)))

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
