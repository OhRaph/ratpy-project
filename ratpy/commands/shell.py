""" Ratpy Command Shell module """

from threading import Thread

from scrapy.shell import Shell
from scrapy.utils.url import guess_scheme
from scrapy.exceptions import UsageError

from ratpy.commands import RatpyCommand, TestEnvironment, TestSpider, set_command

# ############################################################### #
# ############################################################### #


class Command(RatpyCommand):

    """ Ratpy Command Shell class """

    # ####################################################### #
    # ####################################################### #

    name = 'shell'

    requires_project = False
    default_settings = {
        'KEEP_ALIVE': True,
        'LOGSTATS_INTERVAL': 0,
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        }

    # ####################################################### #

    def syntax(self):
        return '<spider> [url|file]'

    def short_desc(self):
        return 'Interactive scraping console.'

    def long_desc(self):
        return 'Interactive console for scraping the given url or file. Use ./file.html syntax or full path for local file.'

    # ####################################################### #

    def add_options(self, parser):
        RatpyCommand.add_options(self, parser)
        parser.add_option('-c', dest='code', help='evaluate the code in the shell, print the result and exit')
        parser.add_option('--no-redirect', dest='no_redirect', action='store_true', default=False, help='do not handle HTTP 3xx status codes and print response as-is')

    def process_options(self, args, opts):
        RatpyCommand.process_options(self, args, opts)

    # ####################################################### #

    def run(self, args, opts):
        set_command(self)

        if len(args) == 1:
            spider, url = args[0], None
        elif len(args) == 2:
            spider, url = args[0], guess_scheme(args[1])
            if spider == '_':
                raise UsageError('No URL needed')
        else:
            raise UsageError()

        self.crawler_process.settings['LOG_STATS_INTERVAL'] = -1

        try:
            spider_cls = self.crawler_process.spider_loader.load(spider) if spider != '_' else ShellSpider
        except KeyError:
            print('Unable to find spider : {}'.format(spider))
            self.exitcode = 1
            return

        crawler = self.crawler_process._create_crawler(spider_cls)
        crawler.engine = crawler._create_engine()
        crawler.engine.start()

        self._start_crawler_thread()

        shell = Shell(crawler, update_vars=self.update_vars, code=opts.code)

        if spider_cls == ShellSpider:
            with TestEnvironment():
                shell.start(ShellSpider.create_random_url(self.crawler_process.settings), redirect=not opts.no_redirect)
        else:
            shell.start(url=url, redirect=not opts.no_redirect)

    # ####################################################### #
    # ####################################################### #

    def update_vars(self, vars):
        pass

    def _start_crawler_thread(self):
        t = Thread(target=self.crawler_process.start, kwargs={'stop_after_crawl': False})
        t.daemon = True
        t.start()

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #


class ShellSpider(TestSpider):

    name = 'ratpy.spider.test.shell'

    def __init__(self, crawler, *args, **kwargs):
        TestSpider.__init__(self, crawler, *args, **kwargs)
        self.start_requests = lambda: []

# ############################################################### #
# ############################################################### #
