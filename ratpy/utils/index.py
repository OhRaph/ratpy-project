""" Ratpy Index module """

import json
import os
import pandas

from ratpy.utils import Logger, sizeof, create_file

# ############################################################### #
# ############################################################### #

DEFAULT_DIR = '../'


class Index(Logger):

    """ Ratpy Index class """

    # ####################################################### #
    # ####################################################### #

    name = 'index'

    crawler = None

    work_path = None

    _columns = None
    _index = None

    # ####################################################### #

    def __init__(self, crawler, *args, name=None, work_dir=DEFAULT_DIR, log_dir=DEFAULT_DIR, columns=None, **kwargs):

        if name:
            self.name = name

        self.crawler = crawler

        self._columns = columns
        self._index = pandas.DataFrame([], columns=self._columns)

        self.work_path = os.path.join(work_dir, self.name+'.csv')
        create_file(self.work_path, 'w+', self._index.to_csv(index=False))

        Logger.__init__(self, self.crawler, log_dir=log_dir)

        # self.logger.info('{:_<18} : OK   \'{}\''.format('Initialisation', self.work_path))

    def __str__(self):
        return self.infos.__str__()

    # ####################################################### #

    @property
    def infos(self):
        infos = super().infos
        infos['work_path'] = self.work_path
        infos['counts'] = self.counts
        return infos

    # ####################################################### #

    def open(self):
        # self.logger.debug('{:_<18}'.format('Open'))
        with open(self.work_path, 'r') as file:
            self._index = pandas.read_csv(file)
            file.close()
        self.logger.debug('{:_<18} : OK   \'{}\''.format('Open', self.work_path))

    def close(self):
        # self.logger.debug('{:_<18}'.format('Close'))
        if self.crawler.settings.get('WORK_ON_DISK', False):
            with open(self.work_path, 'w+') as file:
                file.write(self._index.to_csv(index=False))
                file.close()
        self.logger.debug('{:_<18} : OK   \'{}\''.format('Close', self.work_path))

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

        self.logger.debug('{:_<18} : OK   {}'.format('Index (+)', json.dumps(kwargs, indent=None, sort_keys=False)))

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
