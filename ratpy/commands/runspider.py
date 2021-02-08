""" Ratpy Command RunSpider module """

import sys
import os
from importlib import import_module

from scrapy.utils.spider import iter_spider_classes
from scrapy.exceptions import UsageError
from scrapy.utils.conf import arglist_to_dict
from scrapy.linkextractors import LinkExtractor

from ratpy.commands import RatpyCommand, TestEnvironment, TestSpider, set_command

# ############################################################### #
# ############################################################### #


def _import_file(filepath):
    abspath = os.path.abspath(filepath)
    dirname, file = os.path.split(abspath)
    file_name, file_ext = os.path.splitext(file)
    if file_ext != '.py':
        raise ValueError('Not a Python source file : \'{}\''.format(abspath))
    if dirname:
        sys.path = [dirname] + sys.path
    try:
        module = import_module(file_name)
    finally:
        if dirname:
            sys.path.pop(0)
    return module

# ############################################################### #
# ############################################################### #


class Command(RatpyCommand):

    """ Ratpy Command RunSpider class """

    # ####################################################### #
    # ####################################################### #

    name = 'runspider'

    requires_project = False
    default_settings = {'SPIDER_LOADER_WARN_ONLY': True}

    # ####################################################### #

    def syntax(self):
        return '<spider_file> [options]'

    def short_desc(self):
        return 'Run a self-contained spider.'

    def long_desc(self):
        return 'Run the spider defined in the given file without creating a project.'

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

        spider_file = args[0]
        if spider_file != '_':
            if not os.path.exists(spider_file):
                raise UsageError('File not found : {}\n'.format(spider_file))
            try:
                module = _import_file(spider_file)
            except (ImportError, ValueError):
                raise UsageError('Unable to load file : {}\n'.format(spider_file))
            try:
                spider_cls = list(iter_spider_classes(module)).pop()
            except IndexError:
                raise UsageError('Unable to find spider in file : {}\n'.format(spider_file))
        else:
            spider_cls = RunSpider

        if spider_cls == RunSpider:
            with TestEnvironment():
                self.crawler_process.crawl(spider_cls, **opts.spargs)
                self.crawler_process.start()
        else:
            self.crawler_process.settings['WORK_ON_DISK'] = True
            self.crawler_process.crawl(spider_cls, **opts.spargs)
            self.crawler_process.start()

        if self.crawler_process.bootstrap_failed:
            self.exitcode = 1

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #


import ratpy


class RunSpider(TestSpider):

    name = 'ratpy.spider.test.crawler'

    link_extractor = LinkExtractor()

    def __init__(self, crawler, *args, **kwargs):
        TestSpider.__init__(self, crawler, *args, **kwargs)
        self.start_requests = lambda: [ratpy.Request(url=self.request_url)]

# ############################################################### #
# ############################################################### #
