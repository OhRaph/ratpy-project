
import hashlib

from io import BytesIO
from PIL import Image

from ratpy.config.pipeline.files import FilesPipeline, FileException
from ratpy.http.request import Request
from ratpy.utils import to_bytes, to_md5sum


class ImageException(FileException):
    pass


class ImagesPipeline(FilesPipeline):

    name = 'ratpy.pipeline.medias.images'

    MEDIA_NAME = 'image'

    MIN_WIDTH = 0
    MIN_HEIGHT = 0
    EXPIRES = 45
    THUMBS = {}
    DEFAULT_IMAGES_URLS_FIELD = '_image_urls'
    DEFAULT_IMAGES_RESULTS_FIELD = '_image_results'

    def __init__(self, crawler, store_uri=None):

        FilesPipeline.__init__(self, crawler, store_uri)

        self.expires = self.crawler.settings.getint('IMAGES_EXPIRES', self.EXPIRES)
        self.images_urls_field = self.crawler.settings.get('IMAGES_URLS_FIELD', self.DEFAULT_IMAGES_URLS_FIELD)
        self.images_result_field = self.crawler.settings.get('IMAGES_RESULTS_FIELD', self.DEFAULT_IMAGES_RESULTS_FIELD)
        self.min_width = self.crawler.settings.getint('IMAGES_MIN_WIDTH', self.MIN_WIDTH)
        self.min_height = self.crawler.settings.getint('IMAGES_MIN_HEIGHT', self.MIN_HEIGHT)
        self.thumbs = self.crawler.settings.get('IMAGES_THUMBS', self.THUMBS)

    @classmethod
    def from_crawler(cls, crawler):
        store_uri = crawler.settings.get('IMAGES_STORE', None)
        return cls(crawler, store_uri=store_uri)

    def file_downloaded(self, response, request):
        checksum = None
        for path, image, buf in self.get_images(response, request):
            if checksum is None:
                buf.seek(0)
                checksum = to_md5sum(buf)
            self.store.persist_file(path, buf, self.infos)
        return checksum

    def get_images(self, response, request):
        path = self.file_path(request)
        orig_image = Image.open(BytesIO(response.body))

        width, height = orig_image.size
        if width < self.min_width or height < self.min_height:
            raise ImageException("Image too small ({}x{} < {}x{}x%d)".format(width, height, self.min_width, self.min_height))

        image, buf = self.convert_image(orig_image)
        yield path, image, buf

        for thumb_id, size in self.thumbs.items():
            thumb_path = self.thumb_path(request, thumb_id)
            thumb_image, thumb_buf = self.convert_image(image, size)
            yield thumb_path, thumb_image, thumb_buf

    def convert_image(self, image, size=None):
        if image.format == 'PNG' and image.mode == 'RGBA':
            background = Image.new('RGBA', image.size, (255, 255, 255))
            background.paste(image, image)
            image = background.convert('RGB')
        elif image.mode == 'P':
            image = image.convert("RGBA")
            background = Image.new('RGBA', image.size, (255, 255, 255))
            background.paste(image, image)
            image = background.convert('RGB')
        elif image.mode != 'RGB':
            image = image.convert('RGB')

        if size:
            image = image.copy()
            image.thumbnail(size, Image.ANTIALIAS)

        buf = BytesIO()
        image.save(buf, 'JPEG')
        return image, buf

    def get_media_requests(self, item):
        return [Request(url=url) for url in item.get(self.images_urls_field, [])]

    def item_completed(self, results, item):
        if isinstance(item, dict) or self.images_result_field in item.fields:
            item[self.images_result_field] = [x for ok, x in results if ok]
        return item

    def file_path(self, request):
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return 'full/{}.jpg'.format(image_guid)

    def thumb_path(self, request, thumb_id):
        thumb_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return 'thumbs/{}/{}.jpg'.format(thumb_id, thumb_guid)
