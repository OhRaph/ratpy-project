
import hashlib
import logging
import mimetypes
import os
import time

from collections import defaultdict
from io import BytesIO

from twisted.internet import defer

from ratpy.config.pipeline.media import MediaPipeline
from ratpy.http.request import Request, IgnoreRequest
from ratpy.utils import NotConfigured, to_bytes, to_md5sum


logger = logging.getLogger(__name__)


class FileException(Exception):
    pass


class FSFilesStore(object):
    def __init__(self, basedir):
        if '://' in basedir:
            basedir = basedir.split('://', 1)[1]
        self.basedir = basedir
        self._mkdir(self.basedir)
        self.created_directories = defaultdict(set)

    def persist_file(self, path, buf, info):
        absolute_path = self._get_filesystem_path(path)
        self._mkdir(os.path.dirname(absolute_path), info)
        with open(absolute_path, 'wb') as f:
            f.write(buf.getvalue())

    def stat_file(self, path, info):
        absolute_path = self._get_filesystem_path(path)
        try:
            last_modified = os.path.getmtime(absolute_path)
        except os.error:
            return {}

        with open(absolute_path, 'rb') as f:
            checksum = to_md5sum(f)

        return {'last_modified': last_modified, 'checksum': checksum}

    def _get_filesystem_path(self, path):
        path_comps = path.split('/')
        return os.path.join(self.basedir, *path_comps)

    def _mkdir(self, dirname, domain=None):
        seen = self.created_directories[domain] if domain else set()
        if dirname not in seen:
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            seen.add(dirname)


class FilesPipeline(MediaPipeline):

    name = 'ratpy.pipeline.medias.files'

    MEDIA_NAME = "file"
    EXPIRES = 90
    DEFAULT_FILES_URLS_FIELD = '_file_urls'
    DEFAULT_FILES_RESULTS_FIELD = '_file_results'

    def __init__(self, crawler, store_uri=None):

        self.directory = os.path.join('spider', self.name)
        self.crawler = crawler

        MediaPipeline.__init__(self, self.crawler)

        if store_uri is None:
            raise NotConfigured
        self.store = FSFilesStore(store_uri)

        self.expires = self.crawler.settings.getint('FILES_EXPIRES', self.EXPIRES)
        self.files_urls_field = self.crawler.settings.get('FILES_URLS_FIELD', self.DEFAULT_FILES_URLS_FIELD)
        self.files_results_field = self.crawler.settings.get('FILES_RESULTS_FIELD', self.DEFAULT_FILES_RESULTS_FIELD)

    @classmethod
    def from_crawler(cls, crawler):
        store_uri = crawler.settings.get('FILES_STORE', None)
        return cls(crawler, store_uri=store_uri)

    def media_to_download(self, request):

        def _on_success(result):
            if not result:
                return  # returning None force download

            last_modified = result.get('last_modified', None)
            if not last_modified:
                return  # returning None force download

            age = (time.time() - last_modified) / 60 / 60 / 24
            if age > self.expires >= 0:
                return  # returning None force download

            self.logger.debug(action='Download '+self.MEDIA_NAME, status='SKIP', message='{}'.format(request.url))
            self.inc_stats('up_to_date')

            checksum = result.get('checksum', None)
            return {'url': request.url, 'path': path, 'checksum': checksum}

        path = self.file_path(request)
        dfd = defer.maybeDeferred(self.store.stat_file, path, self.infos)
        dfd.addCallbacks(_on_success, lambda _: None)
        dfd.addErrback(lambda f: self.logger.error(action='Download '+self.MEDIA_NAME, status='FAIL', message='{} --> {} | {}'.format(request.url, f.type, f.value)))
        return dfd

    def get_media_requests(self, item):
        return [Request(url=url) for url in item.get(self.files_urls_field, [])]

    def media_downloaded(self, response, request):

        if response.status != 200:
            self.logger.warning(action='Download '+self.MEDIA_NAME, status='FAIL', message='{}'.format(request.url))
            raise FileException('Download Error')

        if not response.body:
            self.logger.warning(action='Download '+self.MEDIA_NAME, status='EMPTY', message='{}'.format(request.url))
            raise FileException('Download Empty')

        if 'cached' in response.flags:
            self.logger.warning(action='Download '+self.MEDIA_NAME, status='CACHE', message='{}'.format(request.url))
            self.inc_stats('cached')
        else:
            self.logger.info(action='Download '+self.MEDIA_NAME, status='OK', message='{}'.format(request.url))
            self.inc_stats('downloaded')

        try:
            path = self.file_path(request)
            checksum = self.file_downloaded(response, request)
            self.logger.debug(action='Process ' + self.MEDIA_NAME, status='OK', message='{}'.format(request.url))
        except Exception as e:
            self.logger.error(action='Process ' + self.MEDIA_NAME, status='FAIL', message='{}'.format(request.url))
            raise FileException(str(e))

        return {'url': request.url, 'path': path, 'checksum': checksum}

    def media_failed(self, failure, request):
        if not isinstance(failure.value, IgnoreRequest):
            self.logger.warning(action='Downloading ' + self.MEDIA_NAME, status='FAIL', message='{}'.format(request.url))
        raise FileException

    def item_completed(self, results, item):
        if isinstance(item, dict) or self.files_results_field in item.fields:
            item[self.files_results_field] = [x for ok, x in results if ok]
        return item

    def inc_stats(self, status):
        self.crawler.stats.inc_value('pipeline/{}/count'.format(self.MEDIA_NAME), spider=self.spider)
        self.crawler.stats.inc_value('pipeline/{}/{}/count'.format(self.MEDIA_NAME, status), spider=self.spider)

    def file_downloaded(self, response, request):
        path = self.file_path(request)
        buf = BytesIO(response.body)
        checksum = to_md5sum(buf)
        buf.seek(0)
        self.store.persist_file(path, buf, self.infos)
        return checksum

    def file_path(self, request):
        media_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        media_ext = os.path.splitext(request.url)[1]
        if media_ext not in mimetypes.types_map:
            media_ext = ''
            media_type = mimetypes.guess_type(request.url)[0]
            if media_type:
                media_ext = mimetypes.guess_extension(media_type)
        return 'full/%s%s' % (media_guid, media_ext)
