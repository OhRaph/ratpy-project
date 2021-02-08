""" Ratpy Command Bench module """

from scrapy.exceptions import UsageError

from ratpy.commands import RatpyCommand, TestEnvironment, TestSpider, set_command

# ############################################################### #
# ############################################################### #

NB_PAGE = 100
NB_PAGE_LINK = 50


class Command(RatpyCommand):

    """ Ratpy Command Bench class """

    # ####################################################### #
    # ####################################################### #

    name = 'bench'

    requires_project = False
    default_settings = {
        'LOG_LEVEL': 'INFO',
        'LOGSTATS_INTERVAL': 1,
        'CLOSESPIDER_TIMEOUT': 10,
        }

    # ####################################################### #

    def syntax(self):
        return RatpyCommand.syntax(self)

    def short_desc(self):
        return 'Run quick benchmark test.'

    def long_desc(self):
        return RatpyCommand.long_desc(self)

    # ####################################################### #

    def add_options(self, parser):
        RatpyCommand.add_options(self, parser)
        parser.add_option('-m', '--max', dest='max', metavar='VALUE', default=0, help='max number of requests to bench (default: 10000)')
        parser.add_option('-f', '--filter', dest='filter', action='store_true', default=False, help='filter requests')
        parser.add_option('-i', '--interval', dest='interval', metavar='VALUE', default=0, help='override log stats extension interval')

    def process_options(self, args, opts):
        RatpyCommand.process_options(self, args, opts)

        opts.max = int(opts.max)
        if opts.max < 0:
            raise UsageError('Invalid max value')

        opts.interval = int(opts.interval)
        if opts.interval < 0:
            raise UsageError('Invalid interval value')

    # ####################################################### #

    def run(self, args, opts):
        set_command(self)

        if opts.interval > 0:
            self.crawler_process.settings['LOG_STATS_INTERVAL'] = opts.interval

        spider = '_'
        try:
            spider_cls = self.crawler_process.spider_loader.load(spider) if spider != '_' else BenchSpider
        except KeyError:
            print('Unable to find spider : {}'.format(spider))
            self.exitcode = 1
            return

        self.crawler_process.crawl(spider_cls, max_requests=opts.max, filter_requests=opts.filter)

        if spider_cls == BenchSpider:
            with TestEnvironment():
                self.crawler_process.start()
        else:
            self.crawler_process.start()

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #


import ratpy


class BenchSpider(TestSpider):

    name = 'ratpy.spider.test.bencher'

    max = None
    count = 1

    dont_filter = None

    def __init__(self, crawler, *args, max_requests=0, filter_requests=False, **kwargs):
        TestSpider.__init__(self, crawler, *args, **kwargs)
        self.max = max_requests or 10000
        self.dont_filter = not filter_requests
        self.start_requests = lambda: [ratpy.Request(url=self.request_url, dont_filter=self.dont_filter)]

    def parse(self, response, *args, **kwargs):
        for link in self.link_extractor.extract_links(response):
            if self.count < self.max:
                self.count = self.count+1
                url = ratpy.URL(link.url)
                yield ratpy.Request(url=url, dont_filter=self.dont_filter, callback=self.parse)
            else:
                return

# ############################################################### #
# ############################################################### #
