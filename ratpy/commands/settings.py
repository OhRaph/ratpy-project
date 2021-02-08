""" Ratpy Command Settings module """

import json

from scrapy.settings import BaseSettings

from ratpy.commands import RatpyCommand, set_command
from ratpy.utils.display import pprint_python

# ############################################################### #
# ############################################################### #


class Command(RatpyCommand):

    """ Ratpy Command Settings class """

    # ####################################################### #
    # ####################################################### #

    name = 'settings'

    requires_project = False
    default_settings = {
        'LOG_ENABLED': False,
        'SPIDER_LOADER_WARN_ONLY': True
        }

    # ####################################################### #

    def syntax(self):
        return '[options]'

    def short_desc(self):
        return 'Get settings values.'

    def long_desc(self):
        return RatpyCommand.long_desc(self)

    # ####################################################### #

    def add_options(self, parser):
        RatpyCommand.add_options(self, parser)
        parser.add_option('--all', '-a', dest='all', action='store_true', default=False,  help='print all settings')
        parser.add_option('--get', dest='get', metavar='SETTING', help='print raw setting value')
        parser.add_option('--getbool', dest='getbool', metavar='SETTING', help='print setting value, interpreted as a boolean')
        parser.add_option('--getint', dest='getint', metavar='SETTING', help='print setting value, interpreted as an integer')
        parser.add_option('--getfloat', dest='getfloat', metavar='SETTING', help='print setting value, interpreted as a float')
        parser.add_option('--getlist', dest='getlist', metavar='SETTING', help='print setting value, interpreted as a list')
        parser.add_option('--getdict', dest='getdict', metavar='SETTING', help='print setting value, interpreted as a dict')
        parser.add_option('--no-colors', dest='colors', action='store_false', default=True, help='avoid using colors when printing results')

    def process_options(self, args, opts):
        RatpyCommand.process_options(self, args, opts)

    # ####################################################### #

    def run(self, args, opts):
        set_command(self)

        settings = self.crawler_process.settings
        if opts.all:
            pprint_python(settings.copy_to_dict(), colorize=opts.colors)
        else:
            if opts.get:
                s = settings.get(opts.get)
                if isinstance(s, BaseSettings):
                    pprint_python(json.dumps(s.copy_to_dict()), colorize=opts.colors)
                else:
                    print(s)
            elif opts.getbool:
                pprint_python(settings.getbool(opts.getbool), colorize=opts.colors)
            elif opts.getint:
                pprint_python(settings.getint(opts.getint), colorize=opts.colors)
            elif opts.getfloat:
                pprint_python(settings.getfloat(opts.getfloat), colorize=opts.colors)
            elif opts.getlist:
                pprint_python(settings.getlist(opts.getlist), colorize=opts.colors)
            elif opts.getdict:
                pprint_python(settings.getdict(opts.getdict), colorize=opts.colors)

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
