""" Ratpy Command Clean module """

import os

from ratpy.commands import RatpyCommand, set_command

# ############################################################### #
# ############################################################### #


class Command(RatpyCommand):

    """ Ratpy Command Clean class """

    # ####################################################### #
    # ####################################################### #

    name = 'clean'

    requires_project = True
    default_settings = {'LOG_ENABLED': False}

    # ####################################################### #

    def syntax(self):
        RatpyCommand.syntax(self)

    def short_desc(self):
        return 'Clean project.'

    def long_desc(self):
        return 'Clean work directory, log directory and cache files of project.'

    # ####################################################### #

    def add_options(self, parser):
        RatpyCommand.add_options(self, parser)
        parser.add_option('--no-work', dest='work_dir', action='store_false', default=True, help='do not clean work directory')
        parser.add_option('--no-logs', dest='logs_dir', action='store_false', default=True, help='do not clean logs directory')
        parser.add_option('--no-cache', dest='cache', action='store_false', default=True, help='do not clean cache files')

    def process_options(self, args, opts):
        RatpyCommand.process_options(self, args, opts)

    # ####################################################### #

    def run(self, args, opts):
        set_command(self)

        settings = self.crawler_process.settings

        command = 'bash ratpy/utils/resources/clean.sh'
        if opts.work_dir:
            command = command + ' -d \'' + settings.get('WORK_DIR') + '\''
        if opts.logs_dir:
            command = command + ' -d\'' + settings.get('LOG_DIR') + '\''
        if opts.cache:
            command = command + ' -c'

        self.exitcode = os.system(command)

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
