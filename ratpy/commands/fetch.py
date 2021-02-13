""" Ratpy Command Fetch module """

from w3lib.url import is_url

from scrapy.exceptions import UsageError
from scrapy.utils.datatypes import SequenceExclude

import ratpy
from ratpy.commands import RatpyCommand, TestEnvironment, TestSpider, set_command
from ratpy.utils.display import pprint_html, pprint_json

# ############################################################### #
# ############################################################### #


class Command(RatpyCommand):

    """ Ratpy Command Fetch class """

    # ####################################################### #
    # ####################################################### #

    name = 'fetch'

    requires_project = False

    _response = None

    # ####################################################### #

    def syntax(self):
        return '<spider> [url] [options]'

    def short_desc(self):
        return 'Display URL content in terminal.'

    def long_desc(self):
        return 'Display URL content in terminal, using specific spider.'

    # ####################################################### #

    def add_options(self, parser):
        RatpyCommand.add_options(self, parser)
        parser.add_option('--no-redirect', dest='no_redirect', action='store_true', default=False, help='do not handle HTTP 3xx status codes')
        parser.add_option('--no-headers', dest='no_headers', action='store_true', help='do not print request and response headers')
        parser.add_option('--no-body', dest='no_body', action='store_true', help='do not print response body')
        parser.add_option('-f', '--format', dest='format', metavar='FORMAT',  help='output format for response body (html, json, text)')
        parser.add_option('--no-colors', dest='colors', action='store_false', default=True, help='avoid using colors when printing results')

    def process_options(self, args, opts):
        RatpyCommand.process_options(self, args, opts)

    # ####################################################### #

    def run(self, args, opts):
        set_command(self)

        if len(args) == 1:
            spider, url = args[0], None
            if spider != '_':
                raise UsageError('Missing URL')
        elif len(args) == 2:
            spider, url = args[0:2]
            if spider == '_':
                raise UsageError('No URL needed')
            if not is_url(url):
                raise UsageError('Invalid URL')
        else:
            raise UsageError()

        if opts.format and opts.format not in ('html', 'json', 'text'):
            raise UsageError('Invalid output format parameter')

        try:
            spider_cls = self.crawler_process.spider_loader.load(spider) if spider != '_' else FetchSpider
        except KeyError:
            print('Unable to find spider : {}'.format(spider))
            self.exitcode = 1
            return

        if spider_cls == FetchSpider:
            self.crawler_process.crawl(spider_cls, callback=self._save_response)
            with TestEnvironment():
                self.crawler_process.start()
        else:
            request = ratpy.Request(url=url, callback=self._save_response, dont_filter=True)
            if not opts.no_redirect:
                request.meta['handle_httpstatus_list'] = SequenceExclude(range(300, 400))
            else:
                request.meta['handle_httpstatus_all'] = True
            self.crawler_process.crawl(spider_cls, start_requests=lambda: [request])
            self.crawler_process.start()

        self._print_response(opts)

    # ####################################################### #
    # ####################################################### #

    def _save_response(self, response):
        self._response = response

    def _print_response(self, opts):
        if not opts.no_headers:
            print('\n' + '-' * 60)
            print('Request headers :')
            pprint_json(self._response.request.headers.to_unicode_dict(), colorize=opts.colors)
            print('\n' + '-' * 60)
            print('Response headers :')
            pprint_json(self._response.headers.to_unicode_dict(), colorize=opts.colors)

        if not opts.no_body:
            print('\n' + '-' * 60)
            print('Response body :')
            if opts.format:
                if opts.format == 'html':
                    try:
                        pprint_html(self._response.text, colorize=opts.colors)
                    except:
                        print('Unable to print response in HTML !')
                        print(self._response.text)
                elif opts.format == 'json':
                    try:
                        pprint_json(self._response.text, colorize=opts.colors)
                    except:
                        print("Unable to print response in JSON !")
                        print(self._response.text)
                else:
                    print(self._response.text)
            else:
                print(self._response.body)

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #


class FetchSpider(TestSpider):

    name = 'ratpy.spider.test.fetch'

    def __init__(self, crawler, *args, callback=None, **kwargs):
        TestSpider.__init__(self, crawler, *args, **kwargs)
        self.start_requests = lambda: [ratpy.Request(url=self.request_url, callback=callback, dont_filter=True)]

    def parse(self, response, *args, **kwargs):
        yield from []

# ############################################################### #
# ############################################################### #
