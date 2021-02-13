""" Ratpy Command Parse module """

import json

from w3lib.url import is_url

from scrapy.utils.conf import arglist_to_dict
from scrapy.utils.spider import iterate_spider_output
from scrapy.exceptions import UsageError
from scrapy.linkextractors import LinkExtractor

import ratpy
from ratpy.commands import RatpyCommand, TestEnvironment, TestSpider, set_command
from ratpy.utils.display import pprint_python

# ############################################################### #
# ############################################################### #


def _get_callback_from_rules(spider, response):
    if getattr(spider, 'rules', None):
        for rule in spider.rules:
            if rule.link_extractor.matches(response.url):
                return rule.callback or 'parse'
    else:
        print('No CrawlSpider rules found in spider {}, please specify a callback to use for parsing'.format(spider.name))


def _run_callback(response, callback, cb_kwargs=None):
    cb_kwargs = cb_kwargs or {}
    items, requests = [], []

    for x in iterate_spider_output(callback(response, **cb_kwargs)):
        if isinstance(x, (ratpy.Item, dict)):
            items.append(x)
        elif isinstance(x, ratpy.Request):
            requests.append(x)
    return items, requests

# ############################################################### #


class Command(RatpyCommand):

    """ Ratpy Command Parse class """

    # ####################################################### #
    # ####################################################### #

    name = 'parse'

    requires_project = True

    spider = None

    pcrawler = None

    items = {}
    requests = {}

    first_response = None

    # ####################################################### #

    def syntax(self):
        return '<spider> <url> [options]'

    def short_desc(self):
        return 'Parse URL using specific spider and print the results.'

    def long_desc(self):
        return RatpyCommand.long_desc(self)

    # ####################################################### #

    def add_options(self, parser):
        RatpyCommand.add_options(self, parser)
        parser.add_option('-d', '--depth', dest='depth', type='int', default=1, help='maximum depth for parsing requests [default: %default]')
        parser.add_option('-a', '--arg', dest='spargs', action='append', default=[], metavar='NAME=VALUE', help='set spider argument (may be repeated)')
        parser.add_option('-m', '--meta', dest='meta', help='inject extra meta into the Request, it must be a valid raw JSON string')
        parser.add_option('--cb-kwargs', dest='cbkwargs', help='inject extra callback kwargs into the Request, it must be a valid raw JSON string')
        parser.add_option('--no-colors', dest='colors', action='store_false', default=True, help='avoid using colors when printing results')

    def process_options(self, args, opts):
        RatpyCommand.process_options(self, args, opts)
        try:
            opts.spargs = arglist_to_dict(opts.spargs)
        except ValueError:
            raise UsageError('Invalid -a/--arg value')

        if opts.meta:
            try:
                opts.meta = json.loads(opts.meta)
            except ValueError:
                raise UsageError('Invalid -m/--meta value, pass a valid json string.')

        if opts.cbkwargs:
            try:
                opts.cbkwargs = json.loads(opts.cbkwargs)
            except ValueError:
                raise UsageError('Invalid --cbkwargs value, pass a valid json string.')

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

        try:
            spider_cls = self.crawler_process.spider_loader.load(spider) if spider != '_' else ParseSpider
        except KeyError:
            print('Unable to find spider : {}'.format(spider))
            self.exitcode = 1
            return

        if opts.depth <= 0:
            return

        if spider_cls == ParseSpider:
            self.crawler_process.crawl(spider_cls, prepare_request=self._prepare_request, opts=opts)
            self.pcrawler = list(self.crawler_process.crawlers)[0]
            with TestEnvironment():
                self.crawler_process.start()
        else:
            request = ratpy.Request(url=url, cb_kwargs=opts.cbkwargs)
            spider_cls.start_requests = lambda s: [self._prepare_request(s, request, opts)]
            self.crawler_process.crawl(spider_cls, **opts.spargs)
            self.pcrawler = list(self.crawler_process.crawlers)[0]
            self.crawler_process.start()

        self._print_results(url, opts)

    # ####################################################### #
    # ####################################################### #

    @property
    def max_level(self):
        max_items, max_requests = 0, 0
        if self.items:
            max_items = max(self.items)
        if self.requests:
            max_requests = max(self.requests)
        return max(max_items, max_requests)

    def _add_items(self, level, new_items):
        old_items = self.items.get(level, [])
        self.items[level] = old_items + new_items

    def _add_requests(self, level, new_reqs):
        old_reqs = self.requests.get(level, [])
        self.requests[level] = old_reqs + new_reqs

    def _print_items(self, level, colors):
        items = self.items.get(level, [])
        for item in items:
            print('# Scraped Item [{}]'.format(level), '-' * 60)
            pprint_python(dict(item), colorize=colors)

    def _print_requests(self, level, colors):
        requests = self.requests.get(level, [])
        if requests:
            print('# Requests [{}]'.format(level), '-' * 65)
            pprint_python(requests, colorize=colors)

    def _print_results(self, url, opts):
        print('')
        if not self.first_response:
            print('No response downloaded for : {}'.format(url))
        else:
            for level in range(1, self.max_level + 1):
                self._print_items(level, opts.colors)
                self._print_requests(level, opts.colors)

    def _prepare_request(self, spider, request, opts):

        def callback(response, **cb_kwargs):

            if not self.first_response:
                self.first_response = response

            cb_method = getattr(spider, 'parse', None)
            if not callable(cb_method):
                print('Cannot find callback \'parse\' in spider : {}'.format(spider.name))
                return

            depth = response.meta['_depth']

            items, requests = _run_callback(response, cb_method, cb_kwargs)
            self._add_items(depth, items)
            self._add_requests(depth, requests)

            if depth < opts.depth:
                for req in requests:
                    req.meta['_depth'] = depth + 1
                    req.meta['_callback'] = req.callback
                    req.callback = callback
                    req.dont_filter = True
                return requests

        if opts.meta:
            request.meta.update(opts.meta)

        if opts.cbkwargs:
            request.cb_kwargs.update(opts.cbkwargs)

        request.meta['_depth'] = 1
        request.meta['_callback'] = request.callback
        request.callback = callback
        request.dont_filter = True
        return request

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #


class ParseSpider(TestSpider):

    name = 'ratpy.spider.test.fetch'

    link_extractor = LinkExtractor()

    def __init__(self, crawler, *args, prepare_request=None, opts=None, **kwargs):
        TestSpider.__init__(self, crawler, *args, **kwargs)
        self.start_requests = lambda: [prepare_request(self, ratpy.Request(url=self.request_url), opts)]

# ############################################################### #
# ############################################################### #
