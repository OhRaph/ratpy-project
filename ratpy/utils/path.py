""" Ratpy Path module """

import os

__all__ = [
    'resources_directory', 'work_directory', 'log_directory',
    'create_directory', 'create_file'
]

# ############################################################### #
# ############################################################### #


def _get_path_from_settings(settings, name):
    path = settings[name]
    if path and not os.path.exists(path):
        os.makedirs(path)
    return path


def resources_directory(settings):
    return _get_path_from_settings(settings, 'RESOURCES_DIR')


def work_directory(settings):
    return _get_path_from_settings(settings, 'WORK_DIR')


def log_directory(settings):
    return _get_path_from_settings(settings, 'LOG_DIR')

# ############################################################### #


def create_directory(dirpath):

    if not os.path.exists(dirpath):
        os.makedirs(dirpath)


def create_file(filepath, mode='w+', content=''):

    create_directory(os.path.dirname(filepath))

    if not os.path.exists(filepath):
        with open(filepath, mode) as file:
            file.write(content)
            file.close()

# ############################################################### #
# ############################################################### #
