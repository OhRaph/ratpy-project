""" Ratpy Command StartProject module """

import re
import os
import string
from importlib import import_module
from shutil import move, copy2, copystat

from scrapy.utils.template import render_templatefile, string_camelcase
from scrapy.exceptions import UsageError

from ratpy.commands import RatpyCommand, set_command
from ratpy.utils.display import pprint_python

# ############################################################### #
# ############################################################### #

TEMPLATES_TO_RENDER = (
    ('${projectname}', '__init__.py.tmpl'),
    ('${projectname}', 'settings.py.tmpl'),
    ('${projectname}', 'spiders', '__init__.py.tmpl'),
    ('${projectname}', 'extensions', '__init__.py.tmpl'),
    ('${projectname}', 'items', '__init__.py.tmpl'),
    ('${projectname}', 'pipelines', '__init__.py.tmpl'),
    ('${projectname}', 'middlewares', '__init__.py.tmpl'),
)


def is_valid_name(project_name):

    if not re.search(r'^[a-zA-Z_]\w*$', project_name):
        print('Error: Project names must begin with a letter and contain only letters, numbers and underscores')
    else:
        try:
            import_module(project_name)
            print('Error: Module \'{}\' already exists'.format(project_name))
            return False
        except ImportError:
            return True

# ############################################################### #


class Command(RatpyCommand):

    """ Ratpy Command StartProject class """

    # ####################################################### #
    # ####################################################### #

    name = 'startproject'

    requires_project = False
    default_settings = {'LOG_ENABLED': False, 'SPIDER_LOADER_WARN_ONLY': True}

    # ####################################################### #

    def syntax(self):
        return '<name> [directory] [options]'

    def short_desc(self):
        return 'Generate new project.'

    def long_desc(self):
        return 'Generate new project using pre-defined template.'

    # ####################################################### #

    def add_options(self, parser):
        RatpyCommand.add_options(self, parser)
        parser.add_option('-l', '--list', dest='list', action='store_true', help='list available templates')
        parser.add_option('-t', '--template', dest='template', metavar='TEMPLATE', default='basic', help='uses a custom template')

    def process_options(self, args, opts):
        RatpyCommand.process_options(self, args, opts)

    # ####################################################### #

    def run(self, args, opts):
        set_command(self)

        if opts.list:
            self._list_templates(opts.colors)
            return

        if len(args) == 1:
            project_name, project_dir = args[0], args[0]
        elif len(args) == 2:
            project_name, project_dir = args[0], args[1]
        else:
            raise UsageError()

        if not is_valid_name(project_name):
            self.exitcode = 1
            return

        template_dir = self._find_template(opts.template)
        if template_dir:
            self._generate_project(template_dir, project_dir, project_name)

    # ####################################################### #
    # ####################################################### #

    @property
    def templates_dir(self):
        return os.path.join(self.settings['TEMPLATES_DIR'], 'projects')

    def _find_template(self, template):
        template_file = os.path.join(self.templates_dir, template)
        if os.path.exists(template_file):
            return template_file
        else:
            print('Unable to find template : {}'.format(template))
            print('Use \'ratpy startproject --list\' to see all available templates.')
            return None

    def _list_templates(self, colors):
        templates = []
        print('Available templates :')
        for template_name in sorted(os.listdir(self.templates_dir)):
            templates.append(os.path.splitext(template_name)[0])
        pprint_python(templates, colorize=colors)

    def _generate_project(self, template_dir, project_dir, project_name):

        self._copy_tree(template_dir, os.path.abspath(project_dir))
        move(os.path.join(project_dir, 'module'), os.path.join(project_dir, project_name))

        for paths in TEMPLATES_TO_RENDER:
            template_path = os.path.join(*paths)
            template_file = os.path.join(project_dir, string.Template(template_path).substitute(projectname=project_name))
            render_templatefile(template_file, projectname=project_name, ProjectName=string_camelcase(project_name))

        print('New Scrapy project : {}'.format(project_name))
        print('- template directory : {}'.format(template_dir))
        print('- project dirctory : {}\n'.format(os.path.abspath(project_dir)))
        print('You can start your first spider with :')
        print('    cd {}'.format(project_dir))
        print('    ratpy genspider example example.com')

    def _copy_tree(self, source, destination):

        names = os.listdir(source)

        if not os.path.exists(destination):
            os.makedirs(destination)

        for name in names:

            srcname = os.path.join(source, name)
            dstname = os.path.join(destination, name)

            if os.path.isdir(srcname):
                self._copy_tree(srcname, dstname)
            else:
                copy2(srcname, dstname)
        copystat(source, destination)

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
