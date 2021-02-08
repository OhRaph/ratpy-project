""" Ratpy Command List module """

from ratpy.commands import RatpyCommand, set_command
from ratpy.utils.display import pprint_python

# ############################################################### #
# ############################################################### #


class Command(RatpyCommand):

    """ Ratpy Command List class """

    # ####################################################### #
    # ####################################################### #

    name = 'list'

    requires_project = True
    default_settings = {'LOG_ENABLED': False}

    # ####################################################### #

    def syntax(self):
        RatpyCommand.syntax(self)

    def short_desc(self):
        return 'List available spiders.'

    def long_desc(self):
        return RatpyCommand.long_desc(self)

    # ####################################################### #

    def add_options(self, parser):
        RatpyCommand.add_options(self, parser)
        parser.add_option('--no-colors', dest='colors', action='store_false', default=True, help='avoid using colors when printing results')

    def process_options(self, args, opts):
        RatpyCommand.process_options(self, args, opts)

    # ####################################################### #

    def run(self, args, opts):
        set_command(self)

        pprint_python(sorted(self.crawler_process.spider_loader.list()), colorize=opts.colors)

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
