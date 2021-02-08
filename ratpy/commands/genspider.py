"""" Ratpy Command GenSpider module """

import os
import re
import shutil
import string

from importlib import import_module

from scrapy.utils.template import render_templatefile
from scrapy.exceptions import UsageError

from ratpy.commands import RatpyCommand, set_command
from ratpy.utils.display import pprint_python

# ############################################################### #
# ############################################################### #


def sanitize_module_name(module_name):
    module_name = module_name.replace('-', '_').replace('.', '_')
    if module_name[0] not in string.ascii_letters:
        module_name = 'spider_' + module_name
    return module_name

# ############################################################### #


class Command(RatpyCommand):

    """ Ratpy Command GenSpider class """

    # ####################################################### #
    # ####################################################### #

    name = 'genspider'

    requires_project = False
    default_settings = {'LOG_ENABLED': False}

    # ####################################################### #

    def syntax(self):
        return '<name> <start_url> [options]'

    def short_desc(self):
        return 'Generate new spider.'

    def long_desc(self):
        return 'Generate new spider using pre-defined templates.'

    # ####################################################### #

    def add_options(self, parser):
        RatpyCommand.add_options(self, parser)
        parser.add_option('-l', '--list', dest='list', action='store_true', help='list available templates')
        parser.add_option('-e', '--edit', dest='edit', action='store_true', help='edit spider after creating it')
        parser.add_option('-d', '--dump', dest='dump', action='store_true', help='dump template to standard output')
        parser.add_option('-t', '--template', dest='template', metavar='TEMPLATE', default='basic', help='uses a custom template')
        parser.add_option('--force', dest='force', action='store_true', help='overwrite the spider if it exists')
        parser.add_option('--no-colors', dest='colors', action='store_false', default=True, help='avoid using colors when printing results')

    def process_options(self, args, opts):
        RatpyCommand.process_options(self, args, opts)

    # ####################################################### #

    def run(self, args, opts):
        set_command(self)

        if opts.list:
            self._list_templates(opts.colors)
            return

        if opts.dump:
            self._dump_template(opts.template, opts.colors)
            return

        if len(args) != 2:
            raise UsageError()

        spider_name, start_url = args[0:2]

        module_name = sanitize_module_name(spider_name)
        if self.settings.get('BOT_NAME') == module_name:
            print('Cannot create a spider with the same name as your project : {}'.format(module_name))
            return

        try:
            spider_cls = self.crawler_process.spider_loader.load(spider_name)
        except KeyError:
            pass
        else:
            if not opts.force:
                print('Spider \'{}\' already exists in module : {}'.format(spider_name, spider_cls.__module__))
                return

        template_file = self._find_template(opts.template)
        if template_file:
            self._generate_spider(template_file, module_name, spider_name, start_url, opts.template)
            if opts.edit:
                self.exitcode = os.system('scrapy edit \'{}\''.format(spider_name))

    # ####################################################### #
    # ####################################################### #

    @property
    def templates_dir(self):
        return os.path.join(self.settings['TEMPLATES_DIR'], 'spiders')

    def _find_template(self, template):
        template_file = os.path.join(self.templates_dir, '{}.tmpl'.format(template))
        if os.path.exists(template_file):
            return template_file
        else:
            print('Unable to find template : {}'.format(template))
            print('Use \'ratpy genspider --list\' to see all available templates.')
            return None

    def _list_templates(self, colors):
        templates = []
        print('Available templates :')
        for template_name in sorted(os.listdir(self.templates_dir)):
            templates.append(os.path.splitext(template_name)[0])
        pprint_python(templates, colorize=colors)

    def _dump_template(self, template_name, colors):
        template_file = self._find_template(template_name)
        if template_file:
            print('Template file : {}\n'.format(template_file))
            with open(template_file, 'r') as file:
                content = file.read()
                content = re.sub(r'\${([0-9a-z_]*)}', r'your\1', content)
                content = re.sub(r'\${([0-9a-zA-Z_]*)}', r'Your\1', content)
                pprint_python(content, colorize=colors)

    def _generate_spider(self, template_file, module_name, spider_name, start_url, template_name):
        template_vars = {
            'Module': module_name,
            'ClassName': '{}Spider'.format(''.join(s.capitalize() for s in module_name.split('_'))),
            'name': spider_name,
            'StartURL': start_url
        }
        if self.settings.get('NEW_SPIDER_MODULE'):
            spiders_module = import_module(self.settings['NEW_SPIDER_MODULE'])
            spiders_dir = os.path.abspath(os.path.dirname(spiders_module.__file__))
        else:
            spiders_module = None
            spiders_dir = '.'

        spider_file = '{}.py'.format(os.path.join(spiders_dir, module_name))
        shutil.copyfile(template_file, spider_file)
        render_templatefile(spider_file, **template_vars)

        if spiders_module:
            print('Created spider \'{}\' using template \'{}\'  in module :\n  {}.{}'.format(spider_name, template_name, spiders_module.__name__, module_name))
        else:
            print('Created spider \'{}\' using template \'{}\' '.format(spider_name, template_name))

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
