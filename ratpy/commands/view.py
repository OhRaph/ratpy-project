""" Ratpy Command View module """

import os
import tempfile
import webbrowser

from ratpy.commands import fetch
from ratpy.utils.display import pformat_html, pformat_json

# ############################################################### #
# ############################################################### #


class Command(fetch.Command):

    """ Ratpy Command View class """

    # ####################################################### #
    # ####################################################### #

    name = 'view'

    requires_project = False

    browser = None

    # ####################################################### #

    def syntax(self):
        return super(Command, self).syntax()

    def short_desc(self):
        return 'Display URL content in browser.'

    def long_desc(self):
        return 'Display URL content in browser, using specific spider. Browser is defined in command line, else in the BROWSER environment variable, else in the BROWSER setting.'

    # ####################################################### #

    def add_options(self, parser):
        super(Command, self).add_options(parser)
        parser.add_option('-e', '--ext', dest='extension', metavar='EXTENSION', default=None, help='output extension for response body (html, json, text)')
        parser.add_option('--browser', dest='browser', metavar='BROWSER',  default=None, help='browser path or shortcut to use')
        parser.remove_option('--no-colors')

    def process_options(self, args, opts):
        super(Command, self).process_options(args, opts)

    # ####################################################### #

    def run(self, args, opts):
        if opts.browser:
            self.browser = opts.browser
        else:
            try:
                self.browser = os.environ['BROWSER']
            except KeyError:
                self.browser = self.settings.get('BROWSER', None)

        super(Command, self).run(args, opts)

    # ####################################################### #
    # ####################################################### #

    def _print_response(self, opts):

        if not opts.no_headers:
            file, filename = tempfile.mkstemp('.json')
            os.write(file, bytearray(pformat_json(self._response.request.headers.to_unicode_dict(), colorize=False), self._response.encoding))
            os.write(file, bytearray(pformat_json(self._response.headers.to_unicode_dict(), colorize=False), self._response.encoding))
            os.close(file)
            self._open_browser("file://{}".format(filename))

        if not opts.no_body:
            if opts.format:
                if opts.format == 'html':
                    try:
                        file, filename = tempfile.mkstemp('.'+(opts.extension or opts.format))
                        os.write(file, bytearray(pformat_html(self._response.text, colorize=False), self._response.encoding))
                    except:
                        file, filename = tempfile.mkstemp('.text')
                        os.write(file, self._response.body)
                elif opts.format == 'json':
                    try:
                        file, filename = tempfile.mkstemp('.'+(opts.extension or opts.format))
                        os.write(file, bytearray(pformat_json(self._response.text, colorize=False), self._response.encoding))
                    except:
                        file, filename = tempfile.mkstemp('.text')
                        os.write(file, self._response.body)
                else:
                    file, filename = tempfile.mkstemp('.'+(opts.extension or 'text'))
                    os.write(file, self._response.body)
            else:
                file, filename = tempfile.mkstemp('.'+(opts.extension or 'text'))
                os.write(file, self._response.body)
            os.close(file)
            self._open_browser("file://{}".format(filename))

    def _open_browser(self, filename):
        if self.browser:
            webbrowser.GenericBrowser(self.browser).open(filename, 0, True)
        else:
            webbrowser.open(filename, 0, True)

# ############################################################### #
# ############################################################### #
