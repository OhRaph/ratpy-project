""" Ratpy Command Edit module """

import os
import sys

from scrapy.exceptions import UsageError

from ratpy.commands import RatpyCommand, set_command

# ############################################################### #
# ############################################################### #


class Command(RatpyCommand):

    """ Ratpy Command Edit class """

    # ####################################################### #
    # ####################################################### #

    name = 'edit'

    requires_project = True
    default_settings = {'LOG_ENABLED': False}

    editor = None

    # ####################################################### #

    def syntax(self):
        return '<spider>'

    def short_desc(self):
        return 'Edit a spider.'

    def long_desc(self):
        return 'Edit a spider using the editor. Editor defined in command line, else in the EDITOR environment variable, else in the EDITOR setting.'

    # ####################################################### #

    def add_options(self, parser):
        RatpyCommand.add_options(self, parser)
        parser.add_option('--editor', dest='editor', metavar='EDITOR',  default=None, help='path or shortcut of the editor to use')

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
            sys.stderr.write('Spider not found : {}'.format(spider) + os.linesep)
            self.exitcode = 1
            return

        if opts.editor:
            self.editor = opts.editor
        else:
            try:
                self.editor = os.environ['EDITOR']
            except KeyError:
                self.editor = self.settings.get('EDITOR', None)

        filename = sys.modules[spider_cls.__module__].__file__
        filename = filename.replace('.pyc', '.py')

        self._open_editor(filename)

    # ####################################################### #
    # ####################################################### #

    def _open_editor(self, filename):
        if self.editor:
            self.exitcode = os.system('{} \'{}\' &'.format(self.editor, filename))
        else:
            self.exitcode = os.system('gedit \'{}\' &'.format(filename))

# ############################################################### #
# ############################################################### #
