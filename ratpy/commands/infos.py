""" Ratpy Command Infos module """

from scrapy.exceptions import UsageError

from ratpy.commands import RatpyCommand, set_command
from ratpy.utils.display import pprint_json


# ############################################################### #
# ############################################################### #


class Command(RatpyCommand):

    """ Ratpy Command Infos class """

    # ####################################################### #
    # ####################################################### #

    name = 'infos'

    requires_project = False
    default_settings = {'LOG_ENABLED': False}

    _infos = None

    # ####################################################### #

    def syntax(self):
        return '<spider> [options]'

    def short_desc(self):
        return 'Print info about a spider.'

    def long_desc(self):
        return 'Print info about a spider or its components.'

    # ####################################################### #

    def add_options(self, parser):
        RatpyCommand.add_options(self, parser)
        parser.add_option('--subspider', dest='subspiders', action='append', default=[], metavar='NAME', help='print infos of the subspider (may be repeated)')
        parser.add_option('--no-colors', dest='colors', action='store_false', default=True, help='avoid using colors when printing results')

    def process_options(self, args, opts):
        RatpyCommand.process_options(self, args, opts)

    # ####################################################### #

    def run(self, args, opts):
        set_command(self)

        if len(args) != 1:
            raise UsageError()

        spider = args[0]

        try:
            spider_cls = self.crawler_process.spider_loader.load(spider)
        except KeyError:
            print('Unable to find spider : {}'.format(spider))
            self.exitcode = 1
            return

        spider_cls.start_requests = lambda s: self._save_infos(s)

        self.crawler_process.settings['WORK_ON_DISK'] = True
        self.crawler_process.crawl(spider_cls)
        self.crawler_process.start()

        pprint_json(self._infos, colorize=opts.colors)

    # ####################################################### #
    # ####################################################### #

    def _save_infos(self, spider):

        def _save():
            self._infos = {
                'spider': spider.infos,
                'scheduler': spider.crawler.engine.slot.scheduler.infos
                }

        import scrapy
        spider.save_infos = lambda: _save()
        spider.crawler.signals.connect(spider.save_infos, signal=scrapy.signals.spider_opened)

        return []

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
