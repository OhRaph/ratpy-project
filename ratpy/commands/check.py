""" Ratpy Command Check module """

import time

from collections import defaultdict
from unittest import TextTestRunner as TestRunner
from unittest import TextTestResult as TestResult

from scrapy.contracts import ContractsManager
from scrapy.utils.misc import load_object, set_environ
from scrapy.utils.conf import build_component_list

from ratpy.commands import RatpyCommand, set_command

# ############################################################### #
# ############################################################### #


class Command(RatpyCommand):

    """ Ratpy Command Check class """

    # ####################################################### #
    # ####################################################### #

    name = 'check'

    requires_project = True
    default_settings = {'LOG_ENABLED': False}

    # ####################################################### #

    def syntax(self):
        return '<spider> [options]'

    def short_desc(self):
        return 'Check spider contracts.'

    def long_desc(self):
        return RatpyCommand.long_desc(self)

    # ####################################################### #

    def add_options(self, parser):
        RatpyCommand.add_options(self, parser)
        parser.add_option('-l', '--list', dest='list', action='store_true', help='only list contracts, without checking them')
        parser.add_option('-v', '--verbose', dest='verbose', default=False, action='store_true', help='print contract tests for all spiders')

    def process_options(self, args, opts):
        RatpyCommand.process_options(self, args, opts)

    # ####################################################### #

    def run(self, args, opts):
        set_command(self)

        contracts = build_component_list(self.settings.getwithbase('SPIDER_CONTRACTS'))
        conman = ContractsManager(load_object(c) for c in contracts)
        runner = TestRunner(verbosity=2 if opts.verbose else 1)
        result = TextTestResult(runner.stream, runner.descriptions, runner.verbosity)

        contract_reqs = defaultdict(list)

        with set_environ(SCRAPY_CHECK='true'):

            spider = args[0]
            try:
                spider_cls = self.crawler_process.spider_loader.load(spider)
            except KeyError:
                print('Unable to find spider : {}'.format(spider))
                self.exitcode = 1
                return

            spider_cls.start_requests = lambda s: conman.from_spider(s, result)

            tested_methods = conman.tested_methods_from_spidercls(spider_cls)
            if opts.list:
                for method in tested_methods:
                    contract_reqs[spider_cls.name].append(method)
            elif tested_methods:
                self.crawler_process.crawl(spider_cls)

        if opts.list:
            for spider, methods in sorted(contract_reqs.items()):
                if not methods and not opts.verbose:
                    continue
                print(spider)
                for method in sorted(methods):
                    print('  * {}'.format(method))
        else:
            start = time.time()
            self.crawler_process.start()
            stop = time.time()

            result.printErrors()
            result.printSummary(start, stop)
            self.exitcode = int(not result.wasSuccessful())

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #


class TextTestResult(TestResult):

    def printSummary(self, start, stop):
        write = self.stream.write
        writeln = self.stream.writeln

        run = self.testsRun
        plural = 's' if run != 1 else ''

        writeln(self.separator2)
        writeln('Ran {} contract{} in {}s'.format(run, plural, stop - start))
        writeln()

        infos = []
        if not self.wasSuccessful():
            write('FAILED')
            failed, errored = map(len, (self.failures, self.errors))
            if failed:
                infos.append('failures={}'.format(failed))
            if errored:
                infos.append('errors={}'.format(errored))
        else:
            write('OK')

        if infos:
            writeln(' ({})'.format(', '.join(infos)))
        else:
            write('\n')

# ############################################################### #
# ############################################################### #
