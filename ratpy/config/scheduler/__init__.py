""" Ratpy Scheduler module """

import os
import json

from ratpy.utils import Logger, monitored, load_object, create_instance
from ratpy.utils.path import work_directory, create_file

from ratpy.http.url import URL
from ratpy.http.request import Request, IgnoreRequest

# ############################################################### #
# ############################################################### #


@monitored
class RatpyScheduler(Logger):

    """ Ratpy Scheduler class """

    # ####################################################### #
    # ####################################################### #

    name = 'ratpy.scheduler'

    directory = 'scheduler'
    crawler = None
    spider = None

    work_file = None

    dupefilter = None

    q_priority_cls = None
    q_priority = None

    q_memory_cls = None
    q_memory = None

    q_disk_cls = None
    q_disk = None

    # ####################################################### #

    def __init__(self, crawler, dupefilter_class, queues_classes=None):

        self.crawler = crawler
        Logger.__init__(self, self.crawler, directory=self.directory)

        self.work_file = os.path.join(work_directory(self.crawler.settings), self.directory, 'requests.active.json')
        create_file(self.work_file, 'w+', '[]')

        self.dupefilter = create_instance(dupefilter_class, self.crawler.settings, self.crawler, self.directory)

        self.q_priority_cls = queues_classes['priority']
        self.q_memory_cls = queues_classes['memory']
        self.q_disk_cls = queues_classes['disk']

        self.q_disk = self._disk_queue()
        self.q_memory = self._memory_queue()

        self.logger.debug(action='Initialisation', status='OK')

    @classmethod
    def from_crawler(cls, crawler):
        dupefilter_class = load_object(crawler.settings['DUPEFILTER_CLASS'])
        queues_classes = {
            'priority': load_object(crawler.settings['SCHEDULER_PRIORITY_QUEUE']),
            'memory': load_object(crawler.settings['SCHEDULER_MEMORY_QUEUE']),
            'disk': load_object(crawler.settings['SCHEDULER_DISK_QUEUE'])
        }
        return cls(crawler, dupefilter_class=dupefilter_class, queues_classes=queues_classes)

    # ####################################################### #

    @property
    def infos(self):
        infos = super().infos
        infos['work_file'] = self.work_file
        infos['queues'] = {
            'memory': self.q_memory.infos if self.q_memory is not None else {},
            'disk': self.q_disk.infos if self.q_disk is not None else {}
            }
        infos['dupefilter'] = self.dupefilter.infos
        return infos

    # ####################################################### #

    def open(self, spider, *args, **kwargs):
        self.logger.debug(action='Open')

        self.spider = spider

        if self.q_disk is not None:
            self.q_disk.open()
            if len(self.q_disk):
                self.logger.info(action='Resuming Crawl', status='OK', message='[{}]'.format(len(self.q_disk)))
            else:
                self.logger.info(action='Resuming Crawl', status='NO')

        if self.q_memory is not None:
            self.q_memory.open()

        self.dupefilter.open(spider)

        self.logger.info(action='Open', status='OK', message='[{}]'.format(self.spider.name))

    def close(self, reason, *args, **kwargs):
        self.logger.debug(action='Close')

        self.dupefilter.close(reason)

        if self.q_disk is not None:
            state = self.q_disk.close()
            self._write_disk_queue_state(state)

        if self.q_memory is not None:
            self.q_memory.close()

        self.logger.info(action='Close', status='OK', message='[{}]'.format(self.spider.name))

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
                self.crawler.stats.inc_value('scheduler/queues/push/disk', spider=self.spider)
                self.crawler.stats.inc_value('scheduler/queues/push', spider=self.spider)
                self.logger.debug(action='Enqueue', status='OK', message='[{: <8}] {}'.format('DISK', req.url))
                return True

            if self._memory_queue_push(req):
                self.crawler.stats.inc_value('scheduler/queues/push/memory', spider=self.spider)
                self.crawler.stats.inc_value('scheduler/queues/push', spider=self.spider)
                self.logger.debug(action='Enqueue', status='OK', message='[{: <8}] {}'.format('MEMORY', req.url))
                return True

            self.logger.debug(action='Enqueue', status='NO', message='[{: <8}] {}'.format('NO QUEUE', req.url))
            return False

        if not request.dont_filter:

            if self.dupefilter.seen(request):
                self.crawler.stats.inc_value('scheduler/filtered', spider=self.spider)
                self.logger.debug(action='Enqueue', status='NO', message='[{: <8}] {}'.format('SEEN', request.url))
                return False
            else:
                request.__class__ = Request
                url = URL(request.url)
                try:
                    if not self.spider.subspiders.enqueue_request_(request, url, **request.cb_kwargs):
                        raise IgnoreRequest
                except IgnoreRequest:
                    self.logger.debug(action='Enqueue', status='NO', message='[{: <8}] {}'.format('IGNORE', request.url))
                    return False

        return _enqueue(request)

    # ####################################################### #

    def next_request(self):

        def _next():

            req = self._memory_queue_pop()
            if req:
                self.crawler.stats.inc_value('scheduler/queues/pop/memory', spider=self.spider)
                self.crawler.stats.inc_value('scheduler/queues/pop', spider=self.spider)
                self.logger.debug(action='Next', status='OK', message='[{: <8}] {}'.format('MEMORY', req.url))
                return req

            req = self._disk_queue_pop()
            if req:
                self.crawler.stats.inc_value('scheduler/queues/pop/disk', spider=self.spider)
                self.crawler.stats.inc_value('scheduler/queues/pop', spider=self.spider)
                self.logger.debug(action='Next', status='OK', message='[{: <8}] {}'.format('DISK', req.url))
                return req

            self.logger.debug(action='Next', status='NO', message='[{: <8}]'.format('EMPTY'))
            return None

        if self.crawler.settings.get('COMMAND') == 'infos':
            return None

        return _next()

    # ####################################################### #

    def _memory_queue(self):
        return create_instance(self.q_priority_cls, settings=None, crawler=self.crawler, type='memory', queues_cls=self.q_memory_cls, dir=os.path.join(self.directory, 'queues'))

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
        return create_instance(self.q_priority_cls, settings=None, crawler=self.crawler, type='disk', queues_cls=self.q_disk_cls, dir=os.path.join(self.directory, 'queues'), start_prios=state)

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
        with open(self.work_file) as file:
            return json.load(file)

    def _write_disk_queue_state(self, state):
        with open(self.work_file, 'w') as file:
            json.dump(state, file)

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
