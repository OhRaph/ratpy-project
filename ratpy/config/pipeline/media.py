import logging
import os

from collections import defaultdict
from twisted.internet.defer import Deferred, DeferredList, _DefGen_Return
from twisted.python.failure import Failure

from scrapy.utils.defer import mustbe_deferred, defer_result
from scrapy.utils.request import request_fingerprint
from scrapy.utils.misc import arg_to_iter
from scrapy.utils.log import failure_to_exc_info

from ratpy.utils import Logger

logger = logging.getLogger(__name__)


class MediaPipeline(Logger):

    name = 'rapty.pipeline.medias'

    directory = None
    crawler = None
    spider = None

    infos = None

    LOG_FAILED_RESULTS = True

    class Infos:
        def __init__(self):
            self.downloading = set()
            self.downloaded = {}
            self.waiting = defaultdict(list)

    def __init__(self, crawler):

        self.directory = os.path.join('spider', self.name)
        self.crawler = crawler

        Logger.__init__(self, crawler, directory=self.directory)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def open_spider(self, spider):
        self.spider = spider
        self.infos = self.Infos()

    def process_item(self, item, spider):
        requests = arg_to_iter(self.get_media_requests(item))
        dlist = [self._process_request(r) for r in requests]
        dfd = DeferredList(dlist, consumeErrors=True)
        return dfd.addCallback(self.item_completed, item)

    def _process_request(self, request):
        fp = request_fingerprint(request)
        cb = request.callback or (lambda _: _)
        eb = request.errback or (lambda _: _)
        request.callback = None
        request.errback = None

        # Return cached result if request was already seen
        if fp in self.infos.downloaded:
            return defer_result(self.infos.downloaded[fp]).addCallbacks(cb, eb)

        # Otherwise, wait for result
        wad = Deferred().addCallbacks(cb, eb)
        self.infos.waiting[fp].append(wad)

        # Check if request is downloading right now to avoid doing it twice
        if fp in self.infos.downloading:
            return wad

        # Download request checking media_to_download hook output first
        self.infos.downloading.add(fp)
        dfd = mustbe_deferred(self.media_to_download, request)
        dfd.addCallback(self._check_media_to_download, request)
        dfd.addBoth(self._cache_result_and_execute_waiters, fp)
        dfd.addErrback(lambda f: logger.error(f.value, exc_info=failure_to_exc_info(f), extra={'spider': self.spider}))
        return dfd.addBoth(lambda _: wad)  # it must return wad at last

    def _check_media_to_download(self, result, request):
        if result is not None:
            return result

        request.meta['handle_httpstatus_all'] = True
        dfd = self.crawler.engine.download(request, self.spider)
        dfd.addCallbacks(
            callback=self.media_downloaded, callbackArgs=(request,),
            errback=self.media_failed, errbackArgs=(request,))
        return dfd

    def _cache_result_and_execute_waiters(self, result, fp):
        if isinstance(result, Failure):
            # minimize cached information for failure
            result.cleanFailure()
            result.frames = []
            result.stack = None
            context = getattr(result.value, '__context__', None)
            if isinstance(context, _DefGen_Return):
                setattr(result.value, '__context__', None)

        self.infos.downloading.remove(fp)
        self.infos.downloaded[fp] = result
        for wad in self.infos.waiting.pop(fp):
            defer_result(result).chainDeferred(wad)

    def media_to_download(self, request):
        pass

    def get_media_requests(self, item):
        pass

    def media_downloaded(self, response, request):
        return response

    def media_failed(self, failure, request):
        return failure

    def item_completed(self, results, item):
        if self.LOG_FAILED_RESULTS:
            for ok, value in results:
                if not ok:
                    logger.error(
                        '%(class)s found errors processing %(item)s',
                        {'class': self.__class__.__name__, 'item': item},
                        exc_info=failure_to_exc_info(value),
                        extra={'spider': self.spider}
                    )
        return item
