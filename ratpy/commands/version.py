""" Ratpy Command Version module """

import scrapy

from scrapy.utils.versions import scrapy_components_versions

from ratpy.commands import RatpyCommand, set_command
from ratpy.utils.display import pprint_python

# ############################################################### #
# ############################################################### #


class Command(RatpyCommand):

    """ Ratpy Command Version class """

    # ####################################################### #
    # ####################################################### #

    name = 'version'

    default_settings = {
        'LOG_ENABLED': False,
        'SPIDER_LOADER_WARN_ONLY': True
        }

    # ####################################################### #

    def syntax(self):
        return '[-v]'

    def short_desc(self):
        return 'Print version.'

    def long_desc(self):
        return RatpyCommand.long_desc(self)

    # ####################################################### #

    def add_options(self, parser):
        RatpyCommand.add_options(self, parser)
        parser.add_option('--verbose', '-v', dest='verbose', action='store_true', help='also display twisted/python/platform info (useful for bug reports)')
        parser.add_option('--no-colors', dest='colors', action='store_false', default=True, help='avoid using colors when printing results')

    def process_options(self, args, opts):
        RatpyCommand.process_options(self, args, opts)

    # ####################################################### #

    def run(self, args, opts):
        set_command(self)

        if opts.verbose:
            for name, version in scrapy_components_versions():
                pprint_python((name, version), colorize=opts.colors)
        else:
            pprint_python(('Scrapy', scrapy.__version__), colorize=opts.colors)

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
