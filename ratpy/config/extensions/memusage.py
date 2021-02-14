""" Ratpy Memory Usage Extension module """

import pprint
import resource
import socket
import sys

from twisted.internet import task

from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.mail import MailSender
from scrapy.utils.engine import get_engine_status

from ratpy.utils import Logger

# ############################################################### #
# ############################################################### #


class MemoryUsage(Logger):

    """ Ratpy Memory Usage Extension class """

    # ####################################################### #
    # ####################################################### #

    name = 'ratpy.extensions.memusage'

    directory = 'extensions'
    crawler = None

    warned = None
    warning = None
    limit = None
    interval = None

    _mailing_list = None
    _mailer = None

    _tasks = None

    # ####################################################### #

    def __init__(self, crawler):

        if not crawler.settings.getbool('MEMORY_USAGE_ENABLED'):
            raise NotConfigured

        self.crawler = crawler
        Logger.__init__(self, self.crawler, directory=self.directory)

        self.warned = False
        self.warning = self.crawler.settings.getint('MEMORY_USAGE_WARNING_MB')*1024*1024
        self.limit = self.crawler.settings.getint('MEMORY_USAGE_LIMIT_MB')*1024*1024
        self.interval = self.crawler.settings.getfloat('MEMORY_USAGE_CHECK_INTERVAL_SECONDS')

        self._mailing_list = self.crawler.settings.getlist('MEMORY_USAGE_NOTIFY_MAIL')
        self._mailer = MailSender.from_settings(self.crawler.settings)

    @classmethod
    def from_crawler(cls, crawler):
        extension = cls(crawler)
        crawler.signals.connect(extension.open, signal=signals.engine_started)
        crawler.signals.connect(extension.close, signal=signals.engine_stopped)
        return extension

    # ####################################################### #

    def open(self):
        self.logger.debug('{:_<18}'.format('Open'))

        self.crawler.stats.set_value('memusage/startup', self.get_virtual_size())

        self._tasks = []
        _task = task.LoopingCall(self._update)
        self._tasks.append(_task)
        _task.start(self.interval, now=True)

        if self.warning:
            _task = task.LoopingCall(self._check_warning)
            self._tasks.append(_task)
            _task.start(self.interval, now=True)

        if self.limit:
            _task = task.LoopingCall(self._check_limit)
            self._tasks.append(_task)
            _task.start(self.interval, now=True)

        self.logger.info('{:_<18} : OK'.format('Open'))

    def close(self):
        self.logger.debug('{:_<18}'.format('Close'))

        for _task in self._tasks:
            if _task.running:
                _task.stop()

        self.logger.info('{:_<18} : OK'.format('Close'))

    # ####################################################### #
    # ####################################################### #

    @staticmethod
    def get_virtual_size():
        size = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if sys.platform != 'darwin':
            size *= 1024
        return size

    # ####################################################### #

    def _update(self):
        self.crawler.stats.max_value('memusage/max', MemoryUsage.get_virtual_size())

    def _check_warning(self):
        self.logger.debug('{:_<18}'.format('Check Warning'))

        if self.warned:
            self.logger.debug('{:_<18} : OK   [{}]'.format('Check Warning', 'ALREADY REACHED'))
            return

        if MemoryUsage.get_virtual_size() > self.warning:

            self.crawler.stats.set_value('memusage/warning_reached', 1)

            mem = self.warning/1024/1024
            self.logger.warning("Memory usage reached %(memusage)dM", {'memusage': mem}, extra={'crawler': self.crawler})

            if self._mailing_list:
                subject = "%s warning: memory usage reached %dM at %s" % (self.crawler.settings['BOT_NAME'], mem, socket.gethostname())
                self._send_report(subject)
                self.crawler.stats.set_value('memusage/warning_notified', 1)

            self.warned = True

            self.logger.debug('{:_<18} : OK   [{}]'.format('Check Warning', 'REACHED'))
        else:
            self.logger.debug('{:_<18} : OK   [{}]'.format('Check Warning', 'NOT REACHED'))

    def _check_limit(self):
        self.logger.debug('{:_<18}'.format('Check Limit'))

        if MemoryUsage.get_virtual_size() > self.limit:

            self.crawler.stats.set_value('memusage/limit_reached', 1)

            mem = self.limit/1024/1024
            self.logger.error("Memory usage exceeded %(memusage)dM", {'memusage': mem}, extra={'crawler': self.crawler})
            self.logger.info("Shutting down Scrapy...")

            if self._mailing_list:
                subject = "%s limit: memory usage reached %dM at %s" % (self.crawler.settings['BOT_NAME'], mem, socket.gethostname())
                self._send_report(subject)
                self.crawler.stats.set_value('memusage/limit_notified', 1)

            open_spiders = self.crawler.engine.open_spiders
            if open_spiders:
                for spider in open_spiders:
                    self.crawler.engine.close_spider(spider, 'memusage_exceeded')
            else:
                self.crawler.stop()

            self.logger.debug('{:_<18} : OK   [{}]'.format('Check Limit', 'REACHED'))
        else:
            self.logger.debug('{:_<18} : OK   [{}]'.format('Check Limit', 'NOT REACHED'))

    # ####################################################### #

    def _send_report(self, subject):
        self.logger.debug('{:_<18}'.format('Send Report'))

        stats = self.crawler.stats

        s = "Memory usage at engine startup : %dM\r\n" % (stats.get_value('memusage/startup')/1024/1024)
        s += "Maximum memory usage           : %dM\r\n" % (stats.get_value('memusage/max')/1024/1024)
        s += "Current memory usage           : %dM\r\n" % (self.get_virtual_size()/1024/1024)
        s += "ENGINE STATUS ------------------------------------------------------- \r\n"
        s += "\r\n"
        s += pprint.pformat(get_engine_status(self.crawler.engine))
        s += "\r\n"

        self._mailer.send(self._mailing_list, subject, s)

        self.logger.debug('{:_<18} : OK'.format('Send Report'))

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
