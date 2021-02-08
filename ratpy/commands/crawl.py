""" Ratpy Command Crawl module """

from scrapy.exceptions import UsageError
from scrapy.linkextractors import LinkExtractor
from scrapy.utils.conf import arglist_to_dict

from ratpy.commands import RatpyCommand, TestEnvironment, TestSpider, set_command

# ############################################################### #
# ############################################################### #


class Command(RatpyCommand):

    """ Ratpy Command Crawl class """

    # ####################################################### #
    # ####################################################### #

    name = 'crawl'

    requires_project = True

    # ####################################################### #

    def syntax(self):
        return '<spider> [options]'

    def short_desc(self):
        return 'Run a spider.'

    def long_desc(self):
        return RatpyCommand.long_desc(self)

    # ####################################################### #

    def add_options(self, parser):
        RatpyCommand.add_options(self, parser)
        parser.add_option('-a', dest='spargs', action='append', default=[], metavar='NAME=VALUE', help='set spider argument (may be repeated)')
        parser.add_option('-i', '--interval', dest='interval', metavar='VALUE', default=0, help='override log stats extension interval')

    def process_options(self, args, opts):
        RatpyCommand.process_options(self, args, opts)
        try:
            opts.spargs = arglist_to_dict(opts.spargs)
        except ValueError:
            raise UsageError('Invalid -a value, use -a NAME=VALUE', print_help=False)

        opts.interval = int(opts.interval)
        if opts.interval < 0:
            raise UsageError('Invalid interval value')

    # ####################################################### #

    def run(self, args, opts):
        set_command(self)

        if len(args) != 1:
            raise UsageError()

        if opts.interval > 0:
            self.crawler_process.settings['LOG_STATS_INTERVAL'] = opts.interval

        spider = args[0]
        try:
            spider_cls = self.crawler_process.spider_loader.load(spider) if spider != '_' else CrawlSpider
        except KeyError:
            print('Unable to find spider : {}'.format(spider))
            self.exitcode = 1
            return

        if spider_cls == CrawlSpider:
            with TestEnvironment():
                crawl_defer = self.crawler_process.crawl(spider_cls, **opts.spargs)
                if getattr(crawl_defer, 'result', None) is not None and issubclass(crawl_defer.result.type, Exception):
                    self.exitcode = 1
                    return
                self.crawler_process.start()
        else:
            self.crawler_process.settings['WORK_ON_DISK'] = True
            crawl_defer = self.crawler_process.crawl(spider_cls, **opts.spargs)
            if getattr(crawl_defer, 'result', None) is not None and issubclass(crawl_defer.result.type, Exception):
                self.exitcode = 1
                return
            self.crawler_process.start()

        if self.crawler_process.bootstrap_failed or (hasattr(self.crawler_process, 'has_exception') and self.crawler_process.has_exception):
            self.exitcode = 1
            return

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #


import ratpy

# ############################################################### #


class CrawlSpider(TestSpider):

    name = 'ratpy.spider.test.crawler'

    link_extractor = LinkExtractor()

    def __init__(self, crawler, *args, **kwargs):
        TestSpider.__init__(self, crawler, *args, **kwargs)
        self.start_requests = lambda: [ratpy.Request(url=self.request_url)]

# ############################################################### #
# ############################################################### #
