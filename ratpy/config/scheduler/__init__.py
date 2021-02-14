""" Ratpy Scheduler module """

import os
import json

from ratpy.utils import Logger, load_object, create_instance
from ratpy.utils.path import work_directory, log_directory, create_directory

from ratpy.http.url import URL
from ratpy.http.request import Request, IgnoreRequest

# ############################################################### #
# ############################################################### #


class RatpyScheduler(Logger):  # pylint: disable=too-many-instance-attributes

    """ Ratpy Scheduler class """

    # ####################################################### #
    # ####################################################### #

    name = 'ratpy.scheduler'

    crawler = None
    spider = None

    work_dir = None
    log_dir = None

    dupefilter = None

    q_priority_cls = None
    q_priority = None

    q_memory_cls = None
    q_memory = None

    q_disk_cls = None
    q_disk = None

    # ####################################################### #

    def __init__(self, crawler, dupefilter, queues_classes=None):

        self.crawler = crawler

        self.work_dir = os.path.join(work_directory(self.crawler.settings), 'scheduler')
        self.log_dir = os.path.join(log_directory(self.crawler.settings), 'scheduler')

        create_directory(self.work_dir)

        Logger.__init__(self, self.crawler, log_dir=self.log_dir)

        self.dupefilter = dupefilter

        self.q_priority_cls = queues_classes['priority']
        self.q_memory_cls = queues_classes['memory']
        self.q_disk_cls = queues_classes['disk']

        self.q_disk = self._disk_queue()
        self.q_memory = self._memory_queue()

        self.logger.debug('{:_<18} : OK'.format('Initialisation'))

    @classmethod
    def from_crawler(cls, crawler):
        dupefilter_class = load_object(crawler.settings['DUPEFILTER_CLASS'])
        dupefilter = create_instance(dupefilter_class, crawler.settings, crawler)
        queues_classes = {
            'priority': load_object(crawler.settings['SCHEDULER_PRIORITY_QUEUE']),
            'memory': load_object(crawler.settings['SCHEDULER_MEMORY_QUEUE']),
            'disk': load_object(crawler.settings['SCHEDULER_DISK_QUEUE'])
        }
        return cls(crawler, dupefilter, queues_classes=queues_classes)

    # ####################################################### #

    @property
    def infos(self):
        infos = super().infos
        infos['queues'] = {
            'memory': self.q_memory.infos if self.q_memory is not None else {},
            'disk': self.q_disk.infos if self.q_disk is not None else {}
            }
        infos['dupefilter'] = self.dupefilter.infos
        return infos

    # ####################################################### #

    def open(self, spider):
        self.logger.debug('{:_<18}'.format('Open'))

        self.spider = spider

        if self.q_disk is not None:
            self.q_disk.open()
            if len(self.q_disk):
                self.logger.info("Resuming crawl ({} requests scheduled)".format(len(self.q_disk)))

        if self.q_memory is not None:
            self.q_memory.open()

        self.dupefilter.open(spider)

        self.logger.info('{:_<18} : OK   [{}]'.format('Open', self.spider.name))

    def close(self, reason):
        self.logger.debug('{:_<18}'.format('Close'))

        self.dupefilter.close(reason)

        if self.q_disk:
            state = self.q_disk.close()
            self._write_disk_queue_state(state)

        if self.q_memory:
            self.q_memory.close()

        self.logger.info('{:_<18} : OK   [{}]'.format('Close', self.spider.name))

    # ####################################################### #

    def __len__(self):
        if self.crawler.settings.get('COMMAND') == 'infos':
            return 0
        size_q_disk = len(self.q_disk or []) if self.crawler.settings.get('WORK_ON_DISK', False) else 0
        size_q_memory = len(self.q_memory or [])
        return size_q_disk + size_q_memory

    def has_pending_requests(self):
        return len(self) > 0

    # ####################################################### #
    # ####################################################### #

    def enqueue_request(self, request):

        def _enqueue(req):

            if self._disk_queue_push(req):
                self.crawler.stats.inc_value('scheduler/enqueued/disk', spider=self.spider)
                self.crawler.stats.inc_value('scheduler/enqueued', spider=self.spider)
                self.logger.debug('{:_<18} : OK   [{: <8}] \'{}\''.format('Enqueue', 'DISK', req.url))
                return True

            if self._memory_queue_push(req):
                self.crawler.stats.inc_value('scheduler/enqueued/memory', spider=self.spider)
                self.crawler.stats.inc_value('scheduler/enqueued', spider=self.spider)
                self.logger.debug('{:_<18} : OK   [{: <8}] \'{}\''.format('Enqueue', 'MEMORY', req.url))
                return True

            self.logger.debug('{:_<18} : NO   [{: <8}] \'{}\''.format('Enqueue', 'NO QUEUE', req.url))
            return False

        if not request.dont_filter:

            if self.dupefilter.seen(request):
                self.crawler.stats.inc_value('scheduler/filtered', spider=self.spider)
                self.logger.debug('{:_<18} : NO   [{: <8}] \'{}\''.format('Enqueue', 'SEEN', request.url))
                return False
            else:
                request.__class__ = Request
                url = URL(request.url)
                try:
                    if not self.spider.subspiders.enqueue_request_(request, url, **request.cb_kwargs):
                        raise IgnoreRequest
                except IgnoreRequest:
                    self.logger.debug('{:_<18} : NO   [{: <8}] \'{}\''.format('Enqueue', 'IGNORE', request.url))
                    return False

        return _enqueue(request)

    # ####################################################### #

    def next_request(self):

        def _next():

            req = self._memory_queue_pop()
            if req:
                self.crawler.stats.inc_value('scheduler/dequeued/memory', spider=self.spider)
                self.crawler.stats.inc_value('scheduler/dequeued', spider=self.spider)
                self.logger.debug('{:_<18} : OK   [{: <8}] \'{}\''.format('Next', 'MEMORY', req.url))
                return req

            req = self._disk_queue_pop()
            if req:
                self.crawler.stats.inc_value('scheduler/dequeued/disk', spider=self.spider)
                self.crawler.stats.inc_value('scheduler/dequeued', spider=self.spider)
                self.logger.debug('{:_<18} : OK   [{: <8}] \'{}\''.format('Next', 'DISK', req.url))
                return req

            self.logger.debug('{:_<18} : NO   [{: <8}]'.format('Next', 'EMPTY'))
            return None

        if self.crawler.settings.get('COMMAND') == 'infos':
            return None

        return _next()

    # ####################################################### #

    def _memory_queue(self):
        return create_instance(self.q_priority_cls, settings=None, crawler=self.crawler, type='memory', queues_cls=self.q_memory_cls, work_dir='', log_dir=os.path.join(self.log_dir, 'queues'))

    def _memory_queue_push(self, request):
        if self.q_memory is None:
            return False
        try:
            self.q_memory.push(request)
        except ValueError:
            self.crawler.stats.inc_value('scheduler/unserializable', spider=self.spider)
            return False
        return True

    def _memory_queue_pop(self):
        if self.q_memory is None:
            return None
        return self.q_memory.pop()

    # ####################################################### #

    def _disk_queue(self):
        state = self._read_disk_queue_state()
        return create_instance(self.q_priority_cls, settings=None, crawler=self.crawler, type='disk', queues_cls=self.q_disk_cls, work_dir=os.path.join(self.work_dir, 'queues'), log_dir=os.path.join(self.log_dir, 'queues'), start_prios=state)

    def _disk_queue_push(self, request):
        if self.q_disk is None or not self.crawler.settings.get('WORK_ON_DISK', False):
            return False
        try:
            self.q_disk.push(request)
        except ValueError:
            self.crawler.stats.inc_value('scheduler/unserializable', spider=self.spider)
            return False
        return True

    def _disk_queue_pop(self):
        if self.q_disk is None or not self.crawler.settings.get('WORK_ON_DISK', False):
            return None
        return self.q_disk.pop()

    # ####################################################### #

    def _read_disk_queue_state(self):
        path = os.path.join(self.work_dir, 'requests.active.json')
        if not os.path.exists(path):
            return ()
        with open(path) as file:
            return json.load(file)

    def _write_disk_queue_state(self, state):
        with open(os.path.join(self.work_dir, 'requests.active.json'), 'w') as file:
            json.dump(state, file)

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
